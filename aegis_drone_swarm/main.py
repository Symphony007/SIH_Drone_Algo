#!/usr/bin/env python3
"""
Main entry point for the Aegis Drone Swarm simulation.
Run this file to start the simulation.
"""

from simulation.simulation import AegisSimulation

def main():
    """Initialize and run the simulation."""
    print("Starting Aegis Drone Swarm Simulation...")
    print("=== AEGIS PROTOCOL ACTIVATED ===")
    print("Features: Decentralized Auction System, Swarm Intelligence")
    
    # Create simulation instance
    sim = AegisSimulation()
    
    # Run the main loop
    sim.run()
    
    print("Simulation ended.")

if __name__ == "__main__":
    main()