import pygame
import sys
import random
import math
from simulation.models.drone import Drone

class AegisSimulation:
    def __init__(self, width=1200, height=800):  # Increased window size
        """Simulation with enhanced tactical protocols and larger display."""
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AEGIS Drone Swarm Protocol - Enhanced Tactics")
        
        # CLEANER COLOR SCHEME
        self.DARK_BLUE = (5, 15, 30)
        self.PANEL_BG = (25, 35, 60, 220)
        self.TEXT_COLOR = (220, 230, 255)
        self.WARNING_COLOR = (255, 80, 80)
        self.SUCCESS_COLOR = (80, 255, 120)
        self.HUD_COLOR = (0, 180, 255)
        self.ZONE_COLOR = (0, 80, 0)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.frame_count = 0
        
        # Protected zone (adjusted for new height)
        self.protected_zone = pygame.Rect(0, self.height - 150, self.width, 150)
        self.last_line_defense_y = self.height - 200  # Y threshold for last defense
        
        # Drone management
        self.friendly_drones = []
        self.enemy_drones = []
        
        # Enemy spawn management
        self.enemy_spawn_timer = 0
        self.spawn_queue = []
        
        # Balance parameters
        self.min_friendly_ratio = 1.1
        self.auto_spawn = False
        
        # Performance metrics
        self.enemies_neutralized = 0
        self.enemies_breached = 0
        self.total_bids = 0
        self.successful_engagements = 0
        self.friendly_losses = 0
        self.mission_complete = False
        
        # Enhanced breach tracking
        self.last_breach_frame = 0
        self.breach_response_active = False
        self.consecutive_breaches = 0
        
        # Simulation mode
        self.aegis_active = True
        self.show_debug = True
        self.show_roles = True
        
        self.initialize_balanced_forces()
        
        print("ENHANCED TACTICAL AEGIS PROTOCOL INITIALIZED")
        print("✓ Staggered Enemy Spawning")
        print("✓ Last Line of Defense Protocol")
        print("✓ Flanking Wolf-Pack Tactics")

    def initialize_balanced_forces(self):
        """Initialize drones with 10% friendly superiority."""
        self.friendly_drones = []
        self.enemy_drones = []
        
        initial_enemies = 8
        initial_friendlies = max(6, int(initial_enemies * self.min_friendly_ratio))
        
        # Defense positions spread across wider area
        defense_positions = [
            (300, 500), (600, 480), (900, 500),
            (450, 550), (750, 550), (600, 450),
            (400, 600), (800, 600)
        ][:initial_friendlies]
        
        for i, (x, y) in enumerate(defense_positions):
            friendly = Drone(x, y, "friendly", f"F{i}")
            friendly.patrol_point = (x, y)
            self.friendly_drones.append(friendly)
        
        # Stagger initial enemy spawns
        for i in range(initial_enemies):
            self.schedule_enemy_spawn(i * 30, i)  # Stagger by 30 frames
        
        print(f"Initial forces: {len(self.friendly_drones)} friendlies vs {initial_enemies} enemies (staggered spawn)")

    def schedule_enemy_spawn(self, delay_frames, index):
        """Schedule an enemy drone to spawn after a delay."""
        self.spawn_queue.append({
            'frame': self.frame_count + delay_frames,
            'index': index,
            'spawned': False
        })

    def spawn_enemy_drone(self, index):
        """Spawn enemy drone with varied entry patterns across wider area."""
        entry_points = [
            (200, 100), (1000, 100), (600, 50), 
            (300, 80), (900, 80), (100, 120), (1100, 120)
        ]
        
        if index < len(entry_points):
            x, y = entry_points[index]
        else:
            x = random.randint(100, self.width - 100)
            y = random.randint(30, 200)
            
        enemy = Drone(x, y, "enemy", f"E{index}")
        enemy.determination = 0.98
        enemy.aggressiveness = random.uniform(0.9, 1.1)
        
        # Varied enemy behaviors
        if index % 4 == 0:  # Flanking enemies
            enemy.target_x = random.choice([200, 1000])
        elif index % 4 == 1:  # Direct assault
            enemy.target_x = self.width // 2
        else:  # Zig-zag pattern
            enemy.target_x = random.randint(300, 900)
            
        enemy.target_y = self.height - 100  # Aim for protected zone
        
        self.enemy_drones.append(enemy)
        print(f"🚀 Enemy {enemy.id} spawned at ({x}, {y}) - Target: ({enemy.target_x}, {enemy.target_y})")

    def process_spawn_queue(self):
        """Process scheduled enemy spawns."""
        for spawn in self.spawn_queue[:]:
            if not spawn['spawned'] and self.frame_count >= spawn['frame']:
                self.spawn_enemy_drone(spawn['index'])
                spawn['spawned'] = True
                self.spawn_queue.remove(spawn)

    def activate_breach_response(self):
        """Activate breach response protocol across all friendly drones."""
        self.breach_response_active = True
        self.consecutive_breaches += 1
        
        print(f"🚨 ACTIVATING BREACH RESPONSE PROTOCOL (Breach #{self.consecutive_breaches})")
        
        # Tactical reset - clear all assignments and activate response
        for friendly in self.friendly_drones:
            if friendly.health > 0:
                friendly.activate_breach_response(duration=180)
                friendly.assigned_target = None
                friendly.current_bids = {}

    def check_last_line_defense(self):
        """Check if any enemies have crossed the last defense line."""
        critical_enemies = []
        
        for enemy in self.enemy_drones:
            if enemy.health > 0 and enemy.y > self.last_line_defense_y:
                critical_enemies.append(enemy)
        
        if critical_enemies:
            # Find closest friendly for each critical enemy
            for critical_enemy in critical_enemies:
                closest_friendly = None
                min_distance = float('inf')
                
                for friendly in self.friendly_drones:
                    if friendly.health > 0 and not friendly.is_destroyed:
                        distance = friendly.distance_to(critical_enemy)
                        if distance < min_distance:
                            min_distance = distance
                            closest_friendly = friendly
                
                if closest_friendly:
                    # Override all other logic for last defense
                    closest_friendly.assigned_target = critical_enemy.id
                    closest_friendly.target_x = critical_enemy.x
                    closest_friendly.target_y = critical_enemy.y
                    closest_friendly.role = "LAST DEFENSE"
                    closest_friendly.breach_response_mode = True
                    closest_friendly.breach_response_timer = 120
                    
                    print(f"🛡️ LAST DEFENSE: {closest_friendly.id} engaging {critical_enemy.id} at Y={critical_enemy.y:.0f}")

    def maintain_force_balance(self):
        if self.auto_spawn:
            current_ratio = len(self.friendly_drones) / max(1, len(self.enemy_drones))
            
            if current_ratio < self.min_friendly_ratio and len(self.friendly_drones) < 20:
                new_friendly = Drone(
                    random.randint(200, self.width - 200),
                    random.randint(400, 600),
                    "friendly", 
                    f"F{len(self.friendly_drones)}"
                )
                self.friendly_drones.append(new_friendly)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.reset_simulation()
                elif event.key == pygame.K_SPACE:
                    self.add_enemy_drones(3)  # Staggered spawn
                elif event.key == pygame.K_a:
                    self.aegis_active = not self.aegis_active
                    status = "ACTIVE" if self.aegis_active else "STANDBY"
                    self.on_aegis_toggle()
                    print(f"Aegis Protocol: {status}")
                elif event.key == pygame.K_d:
                    self.show_debug = not self.show_debug
                    print(f"Debug View: {'ON' if self.show_debug else 'OFF'}")
                elif event.key == pygame.K_t:
                    self.show_roles = not self.show_roles
                    print(f"Role Display: {'ON' if self.show_roles else 'OFF'}")

    def on_aegis_toggle(self):
        """Handle AEGIS system toggle with visual and behavioral changes."""
        if self.aegis_active:
            # Reactivate AEGIS - clear assignments and reset behavior
            for friendly in self.friendly_drones:
                if friendly.health > 0:
                    friendly.assigned_target = None
                    friendly.current_bids = {}
                    friendly.role = "Patrol"
        else:
            # Deactivate AEGIS - stop all coordinated behavior
            for friendly in self.friendly_drones:
                if friendly.health > 0:
                    friendly.assigned_target = None
                    friendly.current_bids = {}
                    friendly.role = "DISABLED"
                    # Set random patrol points to simulate disorganization
                    friendly.patrol_point = (
                        random.randint(200, self.width - 200),
                        random.randint(300, 600)
                    )

    def add_enemy_drones(self, count):
        """Enhanced enemy deployment with staggered spawning."""
        print(f"🚀 DEPLOYING {count} HOSTILES WITH STAGGERED SPAWNING")
        
        # Clear all assignments to ensure proper response to new threats
        for friendly in self.friendly_drones:
            if friendly.health > 0 and self.aegis_active:
                friendly.assigned_target = None
                friendly.current_bids = {}
        
        # Schedule staggered spawns
        base_index = len(self.enemy_drones)
        for i in range(count):
            delay = i * 45  # Stagger by 45 frames (0.75 seconds)
            self.schedule_enemy_spawn(delay, base_index + i)

    def reset_simulation(self):
        self.enemies_neutralized = 0
        self.enemies_breached = 0
        self.total_bids = 0
        self.successful_engagements = 0
        self.friendly_losses = 0
        self.mission_complete = False
        self.breach_response_active = False
        self.consecutive_breaches = 0
        self.spawn_queue = []
        self.initialize_balanced_forces()
        print("Simulation reset with enhanced tactical protocols")

    def run_aegis_protocol(self):
        if not self.aegis_active:
            # Disorganized behavior when AEGIS is off
            self.run_disorganized_behavior()
            return
            
        self.cleanup_destroyed_drones()
        
        if self.check_mission_complete():
            return
        
        # Check last line of defense before regular protocol
        self.check_last_line_defense()
        
        # Enhanced pre-auction validation
        for friendly in self.friendly_drones:
            if friendly.health > 0:
                friendly.validate_assigned_target(self.enemy_drones)
                friendly.update_breach_response()
        
        # Detect isolated high-priority threats before auction
        self.identify_priority_threats()
        
        # Run auction protocol
        for friendly in self.friendly_drones:
            if friendly.health > 0 and friendly.role != "LAST DEFENSE":
                friendly.participate_in_auction(self.enemy_drones, self.friendly_drones)
                self.total_bids += len(friendly.current_bids)
        
        for friendly in self.friendly_drones:
            if friendly.health > 0 and friendly.role != "LAST DEFENSE":
                friendly.resolve_auctions(self.friendly_drones)
        
        for friendly in self.friendly_drones:
            if friendly.health > 0:
                friendly.execute_assignment(self.enemy_drones, self.friendly_drones)

    def run_disorganized_behavior(self):
        """Simple disorganized behavior when AEGIS is disabled."""
        for friendly in self.friendly_drones:
            if friendly.health > 0 and not friendly.is_destroyed:
                # Basic random patrol behavior
                if random.random() < 0.02:  # Occasionally change direction
                    friendly.target_x = friendly.patrol_point[0] + random.uniform(-100, 100)
                    friendly.target_y = friendly.patrol_point[1] + random.uniform(-50, 50)
                
                # Constrain to reasonable area
                friendly.target_x = max(100, min(self.width - 100, friendly.target_x))
                friendly.target_y = max(200, min(self.height - 200, friendly.target_y))
                
                friendly.move(self.width, self.height)

    def identify_priority_threats(self):
        """Identify isolated threats that need immediate attention."""
        high_priority_threats = []
        
        for enemy in self.enemy_drones:
            if enemy.health > 0 and enemy.y > 400:  # Threats getting close to zone
                covering_friendlies = 0
                for friendly in self.friendly_drones:
                    if (friendly.health > 0 and 
                        friendly.distance_to(enemy) <= friendly.sensor_range):
                        covering_friendlies += 1
                
                if covering_friendlies <= 1 and enemy.y > 450:
                    high_priority_threats.append(enemy)
        
        if high_priority_threats and not self.breach_response_active:
            print(f"⚠️  DETECTED {len(high_priority_threats)} ISOLATED HIGH-PRIORITY THREATS")
            for friendly in self.friendly_drones[:min(3, len(self.friendly_drones))]:
                if friendly.health > 0:
                    friendly.activate_breach_response(duration=90)

    def cleanup_destroyed_drones(self):
        alive_enemies = [e for e in self.enemy_drones if e.health > 0 and not e.is_destroyed]
        destroyed_enemies = len(self.enemy_drones) - len(alive_enemies)
        if destroyed_enemies > 0:
            self.enemy_drones = alive_enemies
        
        alive_friendlies = [f for f in self.friendly_drones if f.health > 0 and not f.is_destroyed]
        destroyed_friendlies = len(self.friendly_drones) - len(alive_friendlies)
        if destroyed_friendlies > 0:
            self.friendly_drones = alive_friendlies
            self.friendly_losses += destroyed_friendlies
            if destroyed_friendlies > 0:
                print(f"💥 CASUALTY REPORT: {destroyed_friendlies} friendly drones lost")

    def check_mission_complete(self):
        active_enemies = len([e for e in self.enemy_drones if e.health > 0])
        active_friendlies = len([f for f in self.friendly_drones if f.health > 0])
        
        if active_enemies == 0 and len(self.spawn_queue) == 0 and not self.mission_complete:
            self.mission_complete = True
            self.breach_response_active = False
            print("🎉 MISSION ACCOMPLISHED! All enemies neutralized!")
            return True
            
        if active_friendlies == 0 and not self.mission_complete:
            self.mission_complete = True
            self.breach_response_active = False
            print("💀 MISSION FAILED! All friendly drones lost!")
            return True
            
        return False

    def update(self):
        self.frame_count += 1
        
        self.process_spawn_queue()  # Handle staggered spawning
        self.maintain_force_balance()
        
        # Update breach response status
        if self.breach_response_active and self.frame_count - self.last_breach_frame > 180:
            self.breach_response_active = False
            self.consecutive_breaches = 0
        
        if self.frame_count % 8 == 0 and not self.mission_complete:
            self.run_aegis_protocol()
        
        for drone in self.friendly_drones + self.enemy_drones:
            if drone.health > 0 and not drone.is_destroyed:
                drone.move(self.width, self.height)
        
        if not self.mission_complete:
            self.check_engagements()
            self.check_breaches()

    def check_engagements(self):
        engagements = []
        
        for friendly in self.friendly_drones:
            if friendly.health > 0 and friendly.assigned_target and friendly.ammo > 0:
                for enemy in self.enemy_drones:
                    if enemy.health > 0 and enemy.id == friendly.assigned_target:
                        engagement_distance = friendly.distance_to(enemy)
                        
                        if engagement_distance <= friendly.engagement_range:
                            engagements.append((friendly, enemy))
                            if random.random() < 0.1:
                                friendly.take_damage(20)
                                if friendly.health <= 0:
                                    print(f"💥 FRIENDLY LOST: {friendly.id} destroyed in combat")
                        break
        
        for friendly, enemy in engagements:
            if enemy in self.enemy_drones and enemy.health > 0:
                enemy.health = 0
                friendly.ammo -= 1
                friendly.neutralized_count += 1
                friendly.assigned_target = None
                self.enemies_neutralized += 1
                self.successful_engagements += 1
                
                print(f"✅ {friendly.role}: {friendly.id} eliminated {enemy.id}")

    def check_breaches(self):
        breaches = []
        
        for enemy in self.enemy_drones:
            if enemy.health > 0 and enemy.y >= self.height - 170:  # Adjusted for new zone size
                breaches.append(enemy)
                self.enemies_breached += 1
                self.last_breach_frame = self.frame_count
                
                if not self.breach_response_active:
                    self.activate_breach_response()
                
                print(f"🚨 CRITICAL BREACH: {enemy.id} reached protected zone!")
        
        for enemy in breaches:
            enemy.health = 0

    def render(self):
        """Enhanced rendering with larger display area."""
        self.screen.fill(self.DARK_BLUE)
        
        # Grid lines removed for cleaner look
        self.draw_protected_zone()
        
        role_font = pygame.font.Font(None, 16)
        for drone in self.friendly_drones + self.enemy_drones:
            drone.draw(self.screen, self.aegis_active)
            if self.show_roles and drone.drone_type == "friendly" and drone.health > 0:
                drone.draw_role_text(self.screen, role_font)
        
        if self.show_debug and self.aegis_active:  # Only show debug when AEGIS is active
            self.draw_debug_info()
        
        self.draw_clean_hud()
        
        # Last defense line visualization
        pygame.draw.line(self.screen, (255, 50, 50), 
                        (0, self.last_line_defense_y), 
                        (self.width, self.last_line_defense_y), 2)
        
        if self.frame_count - self.last_breach_frame < 180:
            self.draw_breach_alert()
        
        if self.mission_complete:
            self.draw_mission_status()
        
        pygame.display.flip()

    def draw_protected_zone(self):
        """Draw protected zone with military styling."""
        pygame.draw.rect(self.screen, self.ZONE_COLOR, self.protected_zone)
        pygame.draw.rect(self.screen, (0, 200, 0), self.protected_zone, 3)
        
        # Zone pattern
        for i in range(0, self.width, 60):
            pygame.draw.line(self.screen, (0, 120, 0), 
                           (i, self.height - 150), (i, self.height), 1)

    def draw_clean_hud(self):
        """HUD adjusted for larger screen."""
        self.draw_panel(20, 20, 350, 240, "TACTICAL OVERVIEW")
        self.draw_panel(self.width - 310, 20, 290, 200, "SYSTEMS STATUS")
        self.draw_panel(20, self.height - 180, 400, 160, "COMMAND CONTROLS")

    def draw_panel(self, x, y, width, height, title):
        panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        panel_surface.fill(self.PANEL_BG)
        self.screen.blit(panel_surface, (x, y))
        
        pygame.draw.rect(self.screen, self.HUD_COLOR, (x, y, width, height), 2)
        
        title_bg = pygame.Surface((width, 25), pygame.SRCALPHA)
        title_bg.fill((0, 0, 0, 150))
        self.screen.blit(title_bg, (x, y))
        
        title_font = pygame.font.Font(None, 22)
        title_text = title_font.render(title, True, self.HUD_COLOR)
        title_rect = title_text.get_rect(center=(x + width//2, y + 12))
        self.screen.blit(title_text, title_rect)
        
        if title == "TACTICAL OVERVIEW":
            self.draw_tactical_overview(x + 15, y + 35)
        elif title == "SYSTEMS STATUS":
            self.draw_systems_status(x + 15, y + 35)
        elif title == "COMMAND CONTROLS":
            self.draw_controls_status(x + 15, y + 35)

    def draw_tactical_overview(self, x, y):
        font = pygame.font.Font(None, 20)
        
        active_friendlies = len([f for f in self.friendly_drones if f.health > 0])
        active_enemies = len([e for e in self.enemy_drones if e.health > 0])
        success_rate = self.get_success_rate()
        
        status_lines = [
            f"FRIENDLY FORCES: {active_friendlies}",
            f"HOSTILE CONTACTS: {active_enemies}",
            f"SPAWN QUEUE: {len(self.spawn_queue)}",
            f"TARGETS NEUTRALIZED: {self.enemies_neutralized}",
            f"SECURITY BREACHES: {self.enemies_breached}",
            f"MISSION SUCCESS: {success_rate:.1f}%",
            f"FRIENDLY LOSSES: {self.friendly_losses}",
            f"LAST DEFENSE: ACTIVE",
            f"AEGIS PROTOCOL: {'ACTIVE' if self.aegis_active else 'STANDBY'}"
        ]
        
        for i, line in enumerate(status_lines):
            color = self.TEXT_COLOR
            if "BREACHES" in line and self.enemies_breached > 0:
                color = self.WARNING_COLOR
            elif "SUCCESS" in line:
                color = self.SUCCESS_COLOR if success_rate > 90 else self.TEXT_COLOR
            elif "LOSSES" in line and self.friendly_losses > 0:
                color = self.WARNING_COLOR
            elif "LAST DEFENSE" in line:
                color = self.WARNING_COLOR
            
            text = font.render(line, True, color)
            self.screen.blit(text, (x, y + i * 22))

    def draw_systems_status(self, x, y):
        font = pygame.font.Font(None, 20)
        
        systems_lines = [
            f"AEGIS PROTOCOL: {'ONLINE' if self.aegis_active else 'OFFLINE'}",
            f"BIDDING SYSTEM: {self.total_bids}",
            f"SENSOR NETWORK: {'ACTIVE' if self.aegis_active else 'OFFLINE'}",
            f"TACTICAL STATUS: {'NOMINAL' if not self.breach_response_active else 'BREACH RESPONSE'}",
            f"ISOLATED THREATS: {self.count_isolated_threats()}",
            f"STAGGERED SPAWN: ACTIVE",
            f"MISSION TIME: {self.frame_count//60}s"
        ]
        
        for i, line in enumerate(systems_lines):
            color = self.SUCCESS_COLOR if "ONLINE" in line or "ACTIVE" in line else self.WARNING_COLOR if "OFFLINE" in line else self.TEXT_COLOR
            text = font.render(line, True, color)
            self.screen.blit(text, (x, y + i * 22))

    def count_isolated_threats(self):
        count = 0
        for enemy in self.enemy_drones:
            if enemy.health > 0 and enemy.y > 450:
                covering_friendlies = 0
                for friendly in self.friendly_drones:
                    if (friendly.health > 0 and 
                        friendly.distance_to(enemy) <= friendly.sensor_range):
                        covering_friendlies += 1
                if covering_friendlies <= 1:
                    count += 1
        return count

    def draw_controls_status(self, x, y):
        font = pygame.font.Font(None, 18)
        
        controls = [
            "T - TOGGLE ROLE DISPLAY",
            "A - TOGGLE AEGIS PROTOCOL", 
            "D - TOGGLE SENSOR VIEW",
            "SPACE - DEPLOY HOSTILES",
            "R - RESET MISSION",
            "ESC - EXIT SIMULATION",
            "",
            "AEGIS OFF: Drones disorganized",
            "AEGIS ON: Auction system active"
        ]
        
        for i, line in enumerate(controls):
            color = self.WARNING_COLOR if "AEGIS OFF" in line else self.SUCCESS_COLOR if "AEGIS ON" in line else self.TEXT_COLOR
            text = font.render(line, True, color)
            self.screen.blit(text, (x, y + i * 20))

    def draw_breach_alert(self):
        alert_font = pygame.font.Font(None, 36)
        status_font = pygame.font.Font(None, 24)
        
        if self.breach_response_active:
            alert_text = alert_font.render("BREACH RESPONSE ACTIVE", True, self.WARNING_COLOR)
            status_text = status_font.render("Last defense protocol engaged", True, self.TEXT_COLOR)
        else:
            alert_text = alert_font.render("SECURITY BREACH DETECTED", True, self.WARNING_COLOR)
            status_text = status_font.render("Tactical response initiated", True, self.TEXT_COLOR)
        
        alert_rect = alert_text.get_rect(center=(self.width//2, 30))
        status_rect = status_text.get_rect(center=(self.width//2, 60))
        
        if (self.frame_count // 10) % 2 == 0 or self.breach_response_active:
            self.screen.blit(alert_text, alert_rect)
            self.screen.blit(status_text, status_rect)

    def draw_mission_status(self):
        mission_font = pygame.font.Font(None, 48)
        subtitle_font = pygame.font.Font(None, 24)
        
        active_enemies = len([e for e in self.enemy_drones if e.health > 0])
        
        if active_enemies == 0 and len(self.spawn_queue) == 0:
            text = mission_font.render("MISSION ACCOMPLISHED", True, self.SUCCESS_COLOR)
            subtitle = subtitle_font.render("All hostile targets neutralized", True, self.TEXT_COLOR)
        else:
            text = mission_font.render("MISSION FAILED", True, self.WARNING_COLOR)
            subtitle = subtitle_font.render("Friendly forces eliminated", True, self.TEXT_COLOR)
        
        text_rect = text.get_rect(center=(self.width//2, self.height//2 - 30))
        subtitle_rect = subtitle.get_rect(center=(self.width//2, self.height//2 + 20))
        
        bg_rect = text_rect.union(subtitle_rect).inflate(40, 40)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        self.screen.blit(bg_surface, bg_rect)
        pygame.draw.rect(self.screen, self.HUD_COLOR, bg_rect, 3)
        
        self.screen.blit(text, text_rect)
        self.screen.blit(subtitle, subtitle_rect)

    def draw_debug_info(self):
        """Draw debug information only when AEGIS is active."""
        debug_font = pygame.font.Font(None, 16)
        
        for friendly in self.friendly_drones:
            if friendly.health <= 0:
                continue
                
            # Sensor range (visible only when AEGIS is active)
            pygame.draw.circle(self.screen, (80, 80, 120, 50), 
                             (int(friendly.x), int(friendly.y)), friendly.sensor_range, 1)
            
            # Bid connections
            for enemy_id, bid_info in friendly.current_bids.items():
                enemy = bid_info['enemy']
                if enemy.health > 0:
                    bid_value = bid_info['bid_value']
                    if bid_value < 50:
                        color = (0, 200, 0)  # Green
                    elif bid_value < 100:
                        color = (200, 200, 0)  # Yellow
                    else:
                        color = (200, 100, 0)  # Orange
                    
                    pygame.draw.line(self.screen, color,
                                   (friendly.x, friendly.y), (enemy.x, enemy.y), 1)

    def get_success_rate(self):
        total_engagements = self.enemies_neutralized + self.enemies_breached
        if total_engagements == 0:
            return 100.0
        return (self.enemies_neutralized / total_engagements) * 100

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()