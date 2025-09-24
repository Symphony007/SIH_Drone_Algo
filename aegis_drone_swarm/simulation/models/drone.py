import pygame
import random
import math
import uuid

class Drone:
    def __init__(self, x, y, drone_type, drone_id=None):
        """
        Enhanced drone with better threat detection and tactical reset.
        """
        self.x = x
        self.y = y
        self.drone_type = drone_type
        self.id = drone_id or str(uuid.uuid4())[:8]
        
        # Physical properties
        self.radius = 8
        self.max_speed = 12.0
        self.acceleration = 1.0
        self.pixels_per_meter = 1.0
        self.max_speed_pixels = (self.max_speed * self.pixels_per_meter) / 60
        
        # Current velocity
        self.velocity_x = 0
        self.velocity_y = 0
        
        # MILITARY COLOR SCHEME
        if drone_type == "friendly":
            self.color = (0, 150, 255)    # Military blue
            self.highlight_color = (100, 200, 255)
        else:
            self.color = (255, 80, 80)    # Military red
            self.highlight_color = (255, 150, 150)
        
        # AEGIS PROTOCOL PROPERTIES
        self.assigned_target = None
        self.sensor_range = 250
        self.engagement_range = 20
        self.ammo = 15
        self.health = 100
        self.is_destroyed = False
        
        # Auction system properties
        self.current_bids = {}
        self.communication_range = 300
        self.role = "Patrol"
        
        # Target positions
        self.target_x = x
        self.target_y = y
        self.patrol_point = (x, y)
        
        # FIX: Enhanced tracking
        self.last_target_status = "active"
        self.breach_response_mode = False
        self.breach_response_timer = 0
        
        # Enhanced enemy behavior
        if drone_type == "enemy":
            self.target_x = random.randint(100, 700)
            self.target_y = 550
            self.aggressiveness = random.uniform(0.8, 1.2)
            self.evasion_chance = 0.1
            self.determination = 0.98
        
        # Performance tracking
        self.neutralized_count = 0
        self.bids_won = 0
        self.bids_lost = 0
        self.interceptions_made = 0

    def apply_physics(self):
        """Apply realistic physics."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            acceleration_factor = self.acceleration
            if self.role == "Interceptor":
                acceleration_factor *= 1.5
            elif self.role == "Guardian":
                acceleration_factor *= 0.8
            
            self.velocity_x += dx * acceleration_factor / 60
            self.velocity_y += dy * acceleration_factor / 60
            
            current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            if current_speed > self.max_speed_pixels:
                scale = self.max_speed_pixels / current_speed
                self.velocity_x *= scale
                self.velocity_y *= scale
        
        self.velocity_x *= 0.97
        self.velocity_y *= 0.97

    def move(self, width, height):
        """Enhanced movement with breach response behavior."""
        if self.is_destroyed:
            return
            
        # FIX: Breach response behavior - more aggressive movement
        if self.breach_response_mode and self.drone_type == "friendly":
            self.acceleration = 1.5  # Faster response during breaches
        else:
            self.acceleration = 1.0
            
        self.apply_physics()
        
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        buffer = self.radius + 5
        self.x = max(buffer, min(width - buffer, self.x))
        self.y = max(buffer, min(height - buffer, self.y))
        
        if self.drone_type == "enemy":
            if random.random() < 0.002:
                self.target_x += random.uniform(-30, 30)
                self.target_x = max(100, min(700, self.target_x))

    def activate_breach_response(self, duration=180):
        """Activate breach response mode for faster reaction."""
        self.breach_response_mode = True
        self.breach_response_timer = duration
        # Clear current assignment to force re-evaluation
        self.assigned_target = None
        self.current_bids = {}

    def update_breach_response(self):
        """Update breach response timer."""
        if self.breach_response_mode:
            self.breach_response_timer -= 1
            if self.breach_response_timer <= 0:
                self.breach_response_mode = False

    def validate_assigned_target(self, enemy_drones):
        """Enhanced target validation with breach detection."""
        if not self.assigned_target:
            return False
            
        # Check if target exists and is alive
        for enemy in enemy_drones:
            if enemy.id == self.assigned_target and enemy.health > 0:
                # FIX: Check if target is close to breaching
                if enemy.y > 400:  # Target is getting close to zone
                    return True
                return True
        
        # Target no longer exists - clear assignment
        self.assigned_target = None
        self.last_target_status = "destroyed"
        return False

    def calculate_interception_point(self, enemy):
        if enemy.drone_type != "enemy" or enemy.health <= 0:
            return None
            
        enemy_speed = math.sqrt(enemy.velocity_x**2 + enemy.velocity_y**2)
        if enemy_speed < 0.1:
            return (enemy.x, enemy.y)
        
        distance = self.distance_to(enemy)
        time_to_intercept = distance / (self.max_speed_pixels * 60)
        
        determination_factor = getattr(enemy, 'determination', 0.9)
        future_x = enemy.x + enemy.velocity_x * time_to_intercept * 60 * determination_factor
        future_y = enemy.y + enemy.velocity_y * time_to_intercept * 60 * determination_factor
        
        future_x = max(50, min(750, future_x))
        future_y = max(50, min(550, future_y))
        
        return (future_x, future_y)

    def calculate_bid(self, enemy_drone, friendly_drones):
        """ENHANCED COST FUNCTION with threat priority for isolated targets."""
        if self.ammo <= 0 or self.health <= 0 or self.is_destroyed:
            return float('inf')
        
        distance = self.distance_to(enemy_drone)
        
        if distance > self.sensor_range or enemy_drone.health <= 0:
            return float('inf')
        
        # FIX: Enhanced threat calculation that identifies isolated high-threat targets
        threat_level = self.calculate_enhanced_threat(enemy_drone, friendly_drones)
        
        cost = distance
        
        # FIX: Significantly increase priority for high-threat targets
        cost *= (1.0 - threat_level * 0.6)  # Increased from 0.4 to 0.6
        
        cost *= (1.0 - (self.ammo / 20.0))
        cost *= (self.health / 100.0)
        
        # FIX: Wolf pack strategy - but don't penalize isolated engagements too much
        nearby_allies = 0
        for other in friendly_drones:
            if (other.id != self.id and other.distance_to(enemy_drone) <= other.sensor_range 
                and other.health > 0 and not other.is_destroyed):
                nearby_allies += 1
        
        # Only apply wolf pack bonus if there are allies, but don't penalize isolation
        if nearby_allies > 0:
            cost *= (1.0 - min(0.3, nearby_allies * 0.1))
        
        # FIX: Breach response bonus - lower costs during breach situations
        if self.breach_response_mode:
            cost *= 0.7  # 30% cost reduction during breach response
        
        if self.assigned_target == enemy_drone.id:
            cost *= 0.3
        
        return cost

    def calculate_enhanced_threat(self, enemy_drone, friendly_drones):
        """Calculate threat level that identifies isolated high-priority targets."""
        base_threat = 1.0 - (enemy_drone.y / 600)  # Normal threat (0 to 1)
        base_threat = max(0.1, min(1.0, base_threat))
        
        # FIX: Detect if this is an isolated threat (no other friendlies nearby)
        isolation_factor = self.calculate_isolation_factor(enemy_drone, friendly_drones)
        
        # FIX: Isolated targets near protected zone are EXTREMELY high priority
        if isolation_factor > 0.7 and enemy_drone.y > 300:
            # This target is isolated and getting close - maximum priority
            enhanced_threat = min(1.0, base_threat * 1.5)
        else:
            enhanced_threat = base_threat
            
        return enhanced_threat

    def calculate_isolation_factor(self, enemy_drone, friendly_drones):
        """Calculate how isolated an enemy drone is from friendly coverage."""
        covering_friendlies = 0
        max_potential_coverage = 0
        
        for friendly in friendly_drones:
            if friendly.health > 0 and not friendly.is_destroyed:
                max_potential_coverage += 1
                if friendly.distance_to(enemy_drone) <= friendly.sensor_range:
                    covering_friendlies += 1
        
        if max_potential_coverage == 0:
            return 1.0  # Completely isolated if no friendlies exist
            
        # Isolation factor: 1.0 = completely isolated, 0.0 = well covered
        isolation_factor = 1.0 - (covering_friendlies / max_potential_coverage)
        return isolation_factor

    def determine_role(self, enemy_drones):
        visible_enemies = self.get_visible_enemies(enemy_drones)
        
        if not visible_enemies:
            self.role = "Patrol"
            return
            
        # FIX: Role determination that accounts for isolated threats
        high_priority_threats = [e for e in visible_enemies if e.y > 350]  # Threats close to zone
        
        if high_priority_threats:
            # If there are high-priority threats near the zone, become Guardian
            self.role = "Guardian"
        elif len(visible_enemies) >= 3:
            self.role = "Swarm"
        else:
            self.role = "Interceptor"
        
        if self.ammo <= 3:
            self.role = "Guardian"
            
    # Add this method to the Drone class for flanking behavior
    def calculate_flanking_position(self, enemy_swarm_center, enemy_primary_direction):
        if not enemy_swarm_center or not enemy_primary_direction:
            return None
        
        # Calculate perpendicular direction for flanking
        flank_distance = 150 

    def participate_in_auction(self, enemy_drones, friendly_drones):
        if self.drone_type != "friendly" or self.health <= 0 or self.is_destroyed:
            return
            
        # FIX: Always clear bids and update breach response
        self.update_breach_response()
        self.current_bids = {}
        
        self.determine_role(enemy_drones)
        visible_enemies = self.get_visible_enemies(enemy_drones)
        
        for enemy in visible_enemies:
            bid = self.calculate_bid(enemy, friendly_drones)
            if bid < float('inf'):
                self.current_bids[enemy.id] = {
                    'bid_value': bid,
                    'enemy': enemy,
                    'interception_point': self.calculate_interception_point(enemy)
                }

    def resolve_auctions(self, friendly_drones):
        if self.drone_type != "friendly" or not self.current_bids or self.health <= 0:
            return
            
        for enemy_id, bid_info in self.current_bids.items():
            my_bid = bid_info['bid_value']
            best_bid = my_bid
            best_drone = self
            
            for other in friendly_drones:
                if other.id == self.id or other.health <= 0 or other.is_destroyed:
                    continue
                    
                if self.distance_to(other) > self.communication_range:
                    continue
                    
                other_bid_info = other.current_bids.get(enemy_id)
                if other_bid_info and other_bid_info['bid_value'] < best_bid:
                    best_bid = other_bid_info['bid_value']
                    best_drone = other
            
            if best_drone.id == self.id:
                self.assigned_target = enemy_id
                self.bids_won += 1
                self.interception_point = bid_info['interception_point']
                
                if self.interception_point:
                    self.target_x, self.target_y = self.interception_point

    def execute_assignment(self, enemy_drones, friendly_drones):
        """FIX: Enhanced assignment with breach response priority."""
        if self.drone_type != "friendly" or self.health <= 0 or self.is_destroyed:
            return "Destroyed"
        
        # FIX: Enhanced target validation
        if not self.validate_assigned_target(enemy_drones):
            self.assigned_target = None
            
        if self.assigned_target:
            target_enemy = None
            for enemy in enemy_drones:
                if enemy.id == self.assigned_target and enemy.health > 0:
                    target_enemy = enemy
                    break
            
            if target_enemy:
                self.interception_point = self.calculate_interception_point(target_enemy)
                if self.interception_point:
                    self.target_x, self.target_y = self.interception_point
                
                engagement_distance = self.distance_to(target_enemy)
                
                if engagement_distance <= self.engagement_range:
                    return "Engaging"
                else:
                    return "Pursuing"
        
        # FIX: Priority system - always go for highest threat first
        visible_enemies = self.get_visible_enemies(enemy_drones)
        
        if visible_enemies:
            # Sort by threat level (closest to protected zone first)
            visible_enemies.sort(key=lambda e: e.y, reverse=True)  # Higher y = closer to zone
            highest_threat = visible_enemies[0]
            
            self.interception_point = self.calculate_interception_point(highest_threat)
            if self.interception_point:
                self.target_x, self.target_y = self.interception_point
                return "Swarming"
        
        # Return to defensive position
        guard_y = 450
        guard_x = self.patrol_point[0]
        self.target_x = guard_x
        self.target_y = guard_y
        return "Patrolling"

    def get_visible_enemies(self, enemy_drones):
        return [e for e in enemy_drones if self.distance_to(e) <= self.sensor_range and e.health > 0]

    def distance_to(self, other_drone):
        return math.sqrt((self.x - other_drone.x)**2 + (self.y - other_drone.y)**2)

    def is_at_target(self, tolerance=20):
        return math.sqrt((self.x - self.target_x)**2 + (self.y - self.target_y)**2) <= tolerance

    def take_damage(self, damage):
        """Apply damage to drone."""
        self.health = max(0, self.health - damage)
        if self.health <= 0:
            self.is_destroyed = True
            self.color = (50, 50, 50)
        return self.is_destroyed

    def draw(self, screen, aegis_active=True):
        """Draw drone with AEGIS status awareness."""
        if self.is_destroyed:
            wreckage_size = 6
            pygame.draw.circle(screen, (50, 50, 50), (int(self.x), int(self.y)), wreckage_size)
            pygame.draw.circle(screen, (30, 30, 30), (int(self.x), int(self.y)), wreckage_size, 1)
            return
        
        if self.health <= 0:
            self.is_destroyed = True
            return
        
        # Only show sensor range and bidding lines when AEGIS is active
        if aegis_active:
            # Draw sensor range (subtle)
            pygame.draw.circle(screen, (80, 80, 120, 50), 
                             (int(self.x), int(self.y)), self.sensor_range, 1)
        
        # DRONE ICONS with breach response indicator
        points = []
        icon_size = 10
        
        if self.drone_type == "friendly":
            angle = math.atan2(self.velocity_y, self.velocity_x) if abs(self.velocity_x) + abs(self.velocity_y) > 0.1 else 0
            points = [
                (self.x + icon_size * math.cos(angle), 
                 self.y + icon_size * math.sin(angle)),
                (self.x + icon_size * math.cos(angle + 2.5), 
                 self.y + icon_size * math.sin(angle + 2.5)),
                (self.x + icon_size * math.cos(angle - 2.5), 
                 self.y + icon_size * math.sin(angle - 2.5))
            ]
            
            # FIX: Breach response visual indicator
            if self.breach_response_mode:
                # Pulsing effect for breach response
                pulse = math.sin(self.breach_response_timer * 0.2) * 3 + 8
                pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), int(pulse), 2)
        else:
            points = [
                (self.x, self.y - icon_size),
                (self.x + icon_size, self.y),
                (self.x, self.y + icon_size),
                (self.x - icon_size, self.y)
            ]
        
        if len(points) >= 3:
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, self.highlight_color, points, 2)
        
        # Direction indicator
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed > 0.5:
            indicator_length = min(12, speed * 8)
            end_x = self.x + (self.velocity_x / speed) * indicator_length
            end_y = self.y + (self.velocity_y / speed) * indicator_length
            pygame.draw.line(screen, (200, 200, 200), 
                           (int(self.x), int(self.y)), 
                           (int(end_x), int(end_y)), 1)
        
        # Status indicator
        indicator_color = (255, 255, 0) if self.assigned_target else (150, 150, 150)
        pygame.draw.circle(screen, indicator_color, (int(self.x), int(self.y)), 2)
        
        # Health bar
        bar_width = 20
        bar_height = 2
        bar_x = self.x - bar_width / 2
        bar_y = self.y - icon_size - 8
        health_ratio = self.health / 100.0
        pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))
        health_color = (0, 255, 0) if health_ratio > 0.7 else (255, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))
        
        # Ammo indicator
        ammo_width = 16
        ammo_height = 1
        ammo_x = self.x - ammo_width / 2
        ammo_y = self.y - icon_size - 5
        ammo_ratio = self.ammo / 15.0
        pygame.draw.rect(screen, (80, 80, 80), (ammo_x, ammo_y, ammo_width, ammo_height))
        ammo_color = (0, 150, 255) if ammo_ratio > 0.3 else (255, 150, 0)
        pygame.draw.rect(screen, ammo_color, (ammo_x, ammo_y, ammo_width * ammo_ratio, ammo_height))

    def draw_role_text(self, screen, font):
        if self.health <= 0 or self.is_destroyed:
            return
            
        role_text = font.render(self.role, True, (220, 220, 220))
        text_rect = role_text.get_rect(center=(int(self.x), int(self.y + 15)))
        
        bg_rect = text_rect.inflate(6, 2)
        pygame.draw.rect(screen, (0, 0, 0, 200), bg_rect)
        pygame.draw.rect(screen, self.color, bg_rect, 1)
        
        screen.blit(role_text, text_rect)