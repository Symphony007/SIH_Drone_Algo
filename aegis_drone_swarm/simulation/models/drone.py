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
        
        # Enhanced tracking
        self.last_target_status = "active"
        self.breach_response_mode = False
        self.breach_response_timer = 0
        
        # Enhanced enemy behavior
        if drone_type == "enemy":
            self.target_x = random.randint(100, 1100)
            self.target_y = 750
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
            elif self.role == "LAST DEFENSE":
                acceleration_factor *= 2.0
            
            # CRITICAL FIX: Increase acceleration if target is behind friendly lines
            if self.drone_type == "friendly" and self.assigned_target:
                # Calculate average friendly position
                avg_friendly_y = self.y  # Start with own position
                friendly_count = 1
                
                # This would need access to other drones, but we'll handle in movement logic
                # For now, use simple heuristic: if target is above us (behind), accelerate faster
                if hasattr(self, 'target_enemy') and self.target_enemy:
                    if self.target_enemy.y < self.y:  # Enemy is behind our lines
                        acceleration_factor *= 1.8  # 80% faster acceleration
            
            self.velocity_x += dx * acceleration_factor / 60
            self.velocity_y += dy * acceleration_factor / 60
            
            current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            if current_speed > self.max_speed_pixels:
                scale = self.max_speed_pixels / current_speed
                self.velocity_x *= scale
                self.velocity_y *= scale
        
        self.velocity_x *= 0.97
        self.velocity_y *= 0.97

    def move(self, width, height, friendly_drones=None):
        """Enhanced movement with breach response behavior."""
        if self.is_destroyed:
            return
            
        # Breach response behavior - more aggressive movement
        if self.breach_response_mode and self.drone_type == "friendly":
            self.acceleration = 1.5
        else:
            self.acceleration = 1.0
            
        # CRITICAL FIX: Accelerate faster if target is behind friendly lines
        if (self.drone_type == "friendly" and self.assigned_target and 
            friendly_drones and len(friendly_drones) > 0):
            
            # Calculate average friendly Y position (front line)
            avg_friendly_y = sum(drone.y for drone in friendly_drones if drone.health > 0) / len(friendly_drones)
            
            # Find our target enemy
            target_behind_lines = False
            if hasattr(self, 'target_enemy') and self.target_enemy:
                if self.target_enemy.y < avg_friendly_y:  # Enemy is behind our front line
                    target_behind_lines = True
            elif self.y < avg_friendly_y:  # We are behind front line
                target_behind_lines = True
                
            if target_behind_lines:
                self.acceleration = 2.0  # Double acceleration for threats behind lines
            
        self.apply_physics()
        
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        buffer = self.radius + 5
        self.x = max(buffer, min(width - buffer, self.x))
        self.y = max(buffer, min(height - buffer, self.y))
        
        if self.drone_type == "enemy":
            if random.random() < 0.002:
                self.target_x += random.uniform(-30, 30)
                self.target_x = max(100, min(1100, self.target_x))

    def activate_breach_response(self, duration=180):
        """Activate breach response mode for faster reaction."""
        self.breach_response_mode = True
        self.breach_response_timer = duration
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
            
        for enemy in enemy_drones:
            if enemy.id == self.assigned_target and enemy.health > 0:
                self.target_enemy = enemy  # Store reference for movement logic
                return True
        
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
        
        future_x = max(50, min(1150, future_x))
        future_y = max(50, min(750, future_y))
        
        return (future_x, future_y)

    def calculate_bid(self, enemy_drone, friendly_drones):
        """REVOLUTIONARY COST FUNCTION - Prioritizes isolated threats over clustered ones."""
        if self.ammo <= 0 or self.health <= 0 or self.is_destroyed:
            return float('inf')
        
        distance = self.distance_to(enemy_drone)
        
        if distance > self.sensor_range or enemy_drone.health <= 0:
            return float('inf')
        
        # CRITICAL FIX: Calculate how isolated this enemy is
        isolation_level = self.calculate_isolation_level(enemy_drone, friendly_drones)
        
        # CRITICAL FIX: Calculate how many drones are already targeting this enemy
        current_targeters = self.count_targeters(enemy_drone, friendly_drones)
        
        # CRITICAL FIX: Calculate threat priority (enemies behind lines get highest priority)
        threat_priority = self.calculate_threat_priority(enemy_drone, friendly_drones)
        
        # BASE COST: Distance (but much less important now)
        cost = distance * 0.3  # Reduce distance weighting
        
        # ISOLATION BONUS: Isolated enemies get massive priority
        # If enemy is isolated (few friendlies nearby), drastically reduce cost
        isolation_bonus = 1.0 - (isolation_level * 0.8)  # Up to 80% cost reduction
        cost *= isolation_bonus
        
        # OVER-TARGETING PENALTY: If too many drones are on this target, increase cost
        if current_targeters >= 1:  # Even 1 other targeter reduces priority
            over_targeting_penalty = 1.0 + (current_targeters * 0.8)  # 80% penalty per extra targeter
            cost *= over_targeting_penalty
        
        # THREAT PRIORITY BONUS: Enemies behind lines or close to zone get priority
        threat_bonus = 1.0 - (threat_priority * 0.6)  # Up to 60% cost reduction
        cost *= threat_bonus
        
        # Ammo and health considerations (secondary)
        cost *= (1.0 - (self.ammo / 30.0))  # Reduced effect
        cost *= (self.health / 100.0)
        
        # Breach response bonus
        if self.breach_response_mode:
            cost *= 0.6  # 40% cost reduction during breach response
        
        # Commitment bonus - if we're already on this target
        if self.assigned_target == enemy_drone.id:
            cost *= 0.2  # Strong preference to continue
        
        return max(0.1, cost)  # Ensure cost is never zero

    def calculate_isolation_level(self, enemy_drone, friendly_drones):
        """
        Calculate how isolated an enemy is from friendly coverage.
        Returns 1.0 if completely isolated, 0.0 if well covered.
        """
        covering_friendlies = 0
        total_friendlies = 0
        
        for friendly in friendly_drones:
            if friendly.health > 0 and not friendly.is_destroyed:
                total_friendlies += 1
                if friendly.distance_to(enemy_drone) <= friendly.sensor_range:
                    covering_friendlies += 1
        
        if total_friendlies == 0:
            return 1.0  # Completely isolated
        
        # Isolation level: 1.0 = no coverage, 0.0 = full coverage
        isolation_level = 1.0 - (covering_friendlies / max(1, total_friendlies))
        
        # Boost isolation level if enemy is behind friendly lines
        avg_friendly_y = self.calculate_average_friendly_y(friendly_drones)
        if enemy_drone.y < avg_friendly_y:  # Enemy is behind our lines
            isolation_level = min(1.0, isolation_level * 1.5)  # 50% boost
        
        return isolation_level

    def calculate_threat_priority(self, enemy_drone, friendly_drones):
        """
        Calculate threat priority (0.0 to 1.0) considering multiple factors.
        """
        avg_friendly_y = self.calculate_average_friendly_y(friendly_drones)
        
        # Factor 1: Enemy behind friendly lines (HIGHEST PRIORITY)
        behind_lines_bonus = 0.0
        if enemy_drone.y < avg_friendly_y:
            behind_lines_bonus = 0.6  # 60% bonus for enemies behind lines
        
        # Factor 2: Proximity to protected zone
        zone_proximity = 1.0 - (enemy_drone.y / 800)  # Closer to zone = higher threat
        zone_proximity = max(0.1, zone_proximity) * 0.3  # 30% weight
        
        # Factor 3: Speed threat
        enemy_speed = math.sqrt(enemy_drone.velocity_x**2 + enemy_drone.velocity_y**2)
        speed_threat = min(1.0, enemy_speed / 5.0) * 0.1  # 10% weight
        
        return min(1.0, behind_lines_bonus + zone_proximity + speed_threat)

    def calculate_average_friendly_y(self, friendly_drones):
        """Calculate average Y position of friendly drones (front line)."""
        if not friendly_drones:
            return self.y
        
        active_friendlies = [f for f in friendly_drones if f.health > 0 and not f.is_destroyed]
        if not active_friendlies:
            return self.y
        
        return sum(f.y for f in active_friendlies) / len(active_friendlies)

    def count_targeters(self, enemy_drone, friendly_drones):
        """Count how many friendly drones are targeting this enemy."""
        targeters = 0
        for friendly in friendly_drones:
            if (friendly.health > 0 and not friendly.is_destroyed and 
                friendly.assigned_target == enemy_drone.id):
                targeters += 1
        return targeters

    def determine_role(self, enemy_drones):
        visible_enemies = self.get_visible_enemies(enemy_drones)
        
        if not visible_enemies:
            self.role = "Patrol"
            return
            
        high_priority_threats = [e for e in visible_enemies if e.y > 500]
        
        if high_priority_threats:
            self.role = "Guardian"
        elif len(visible_enemies) >= 3:
            self.role = "Swarm"
        else:
            self.role = "Interceptor"
        
        if self.ammo <= 3:
            self.role = "Guardian"

    def participate_in_auction(self, enemy_drones, friendly_drones):
        if self.drone_type != "friendly" or self.health <= 0 or self.is_destroyed:
            return
            
        self.update_breach_response()
        self.current_bids = {}
        
        self.determine_role(enemy_drones)
        visible_enemies = self.get_visible_enemies(enemy_drones)
        
        # CRITICAL FIX: Sort enemies by isolation level before bidding
        # This ensures we consider the most isolated threats first
        if visible_enemies:
            # Create list of enemies with their isolation levels
            enemy_isolation_pairs = []
            for enemy in visible_enemies:
                isolation = self.calculate_isolation_level(enemy, friendly_drones)
                enemy_isolation_pairs.append((enemy, isolation))
            
            # Sort by isolation level (most isolated first)
            enemy_isolation_pairs.sort(key=lambda x: x[1], reverse=True)
            
            # Bid on enemies in order of isolation
            for enemy, isolation in enemy_isolation_pairs:
                bid = self.calculate_bid(enemy, friendly_drones)
                if bid < float('inf'):
                    self.current_bids[enemy.id] = {
                        'bid_value': bid,
                        'enemy': enemy,
                        'interception_point': self.calculate_interception_point(enemy),
                        'isolation_level': isolation
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
                self.target_enemy = bid_info['enemy']  # Store for movement logic
                self.bids_won += 1
                self.interception_point = bid_info['interception_point']
                
                if self.interception_point:
                    self.target_x, self.target_y = self.interception_point

    def execute_assignment(self, enemy_drones, friendly_drones):
        """REVOLUTIONARY assignment logic - prevents flanking at all costs."""
        if self.drone_type != "friendly" or self.health <= 0 or self.is_destroyed:
            return "Destroyed"
        
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
        
        # ULTIMATE FIX: Smart target selection that prevents flanking
        visible_enemies = self.get_visible_enemies(enemy_drones)
        
        if visible_enemies:
            # Calculate threat scores for each enemy
            enemy_scores = []
            for enemy in visible_enemies:
                # Score based on isolation and threat priority
                isolation = self.calculate_isolation_level(enemy, friendly_drones)
                threat_priority = self.calculate_threat_priority(enemy, friendly_drones)
                targeters = self.count_targeters(enemy, friendly_drones)
                
                # CRITICAL: Score higher for isolated enemies with few targeters
                score = (isolation * 0.6) + (threat_priority * 0.4) - (targeters * 0.3)
                enemy_scores.append((enemy, score))
            
            # Sort by score (highest first)
            enemy_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select the highest scoring enemy that's not over-targeted
            best_target = None
            for enemy, score in enemy_scores:
                targeters = self.count_targeters(enemy, friendly_drones)
                if targeters < 2 or score > 0.7:  # Allow targeting if score is very high
                    best_target = enemy
                    break
            
            if not best_target and enemy_scores:  # Fallback to highest score
                best_target = enemy_scores[0][0]
            
            if best_target:
                self.interception_point = self.calculate_interception_point(best_target)
                if self.interception_point:
                    self.target_x, self.target_y = self.interception_point
                self.assigned_target = best_target.id
                self.target_enemy = best_target
                return "Swarming"
        
        # Return to defensive position
        guard_y = 550
        guard_x = self.patrol_point[0]
        self.target_x = guard_x
        self.target_y = guard_y
        return "Patrolling"

    def get_visible_enemies(self, enemy_drones):
        return [e for e in enemy_drones if self.distance_to(e) <= self.sensor_range and e.health > 0]

    def distance_to(self, other_drone):
        return math.sqrt((self.x - other_drone.x)**2 + (self.y - other_drone.y)**2)

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
        
        if aegis_active and self.drone_type == "friendly":
            pygame.draw.circle(screen, (80, 80, 120, 50), 
                             (int(self.x), int(self.y)), self.sensor_range, 1)
        
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
            
            if self.breach_response_mode:
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
        
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed > 0.5:
            indicator_length = min(12, speed * 8)
            end_x = self.x + (self.velocity_x / speed) * indicator_length
            end_y = self.y + (self.velocity_y / speed) * indicator_length
            pygame.draw.line(screen, (200, 200, 200), 
                           (int(self.x), int(self.y)), 
                           (int(end_x), int(end_y)), 1)
        
        indicator_color = (255, 255, 0) if self.assigned_target else (150, 150, 150)
        pygame.draw.circle(screen, indicator_color, (int(self.x), int(self.y)), 2)
        
        bar_width = 20
        bar_height = 2
        bar_x = self.x - bar_width / 2
        bar_y = self.y - icon_size - 8
        health_ratio = self.health / 100.0
        pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))
        health_color = (0, 255, 0) if health_ratio > 0.7 else (255, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))
        
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