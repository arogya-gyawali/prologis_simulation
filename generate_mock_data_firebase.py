import firebase_admin
from firebase_admin import credentials, firestore
import time
import random
from datetime import date, datetime

# --- Configuration ---
UPDATE_INTERVAL = 5 # How often to update data (in seconds)

# --- Helper Functions (No change here) ---

def get_slight_change(value, min_val, max_val, max_change=0.5):
    change = random.uniform(-max_change, max_change)
    new_value = value + change
    return round(max(min_val, min(max_val, new_value)), 2)

def calculate_ai_safety_score(incidents, faults, anomalies):
    base_score = 100
    score = base_score - (incidents * 3) - (faults * 1.5) - (anomalies * 1)
    return round(max(70, min(100, score)), 2)

# --- Main Simulation (MODIFIED) ---

def run_simulation(db):
    print("🚀 Starting data simulation... Press CTRL+C to stop.")
    
    facility_ids = [
        'facility_sfo_01', 
        'facility_dal_02', 
        'facility_atl_03', 
        'facility_sea_04_dc' # The Data Center
    ]

    try:
        while True:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] --- Starting new 5-second update cycle ---")
            today_str = date.today().isoformat()
            
            # --- 1. CREATE/UPDATE FACILITIES (MAIN DOCS) ---
            # This part is now wrapped in a try/except
            try:
                # Facility 1: Bay Area
                db.collection('facilities').document(facility_ids[0]).set({
                    'name': 'Bay Area Logistics Hub', 'type': 'Warehouse', 'location': 'San Francisco, CA', 'size_sqft': 120000, 'status': 'Operational'
                }, merge=True)

                # Facility 2: Dallas
                db.collection('facilities').document(facility_ids[1]).set({
                    'name': 'Dallas Mega Center', 'type': 'Distribution Hub', 'location': 'Dallas, TX', 'size_sqft': 300000, 'status': 'Operational'
                }, merge=True)

                # Facility 3: Atlanta
                db.collection('facilities').document(facility_ids[2]).set({
                    'name': 'Atlanta Smart Facility', 'type': 'Warehouse', 'location': 'Atlanta, GA', 'size_sqft': 150000, 'status': 'Operational'
                }, merge=True)

                # Facility 4: Seattle Data Center
                db.collection('facilities').document(facility_ids[3]).set({
                    'name': 'Seattle AI Data Center', 'type': 'Data Center', 'location': 'Seattle, WA', 'size_sqft': 500000, 'status': 'Operational',
                    'power_capacity_mw': 150.0, 'cooling_efficiency': 1.15
                }, merge=True)
                
                print("    ✅ Successfully created/set main facility docs.")

            except Exception as e:
                print(f"    ❌ ERROR setting main facility docs: {e}")
                time.sleep(UPDATE_INTERVAL)
                continue # Skip to the next loop cycle

            
            # --- 2. UPDATE DYNAMIC DATA FOR *EACH* FACILITY ---
            
            for fid in facility_ids:
                try:
                    # --- A. Update Sensors (Sub-collection) ---
                    temp_val = get_slight_change(22.0, 15, 28, max_change=0.2)
                    db.collection('facilities').document(fid).collection('sensors').document('temp_01').set({
                        'sensor_type': 'Temperature', 'current_value': temp_val, 'unit': 'C', 'last_updated': firestore.SERVER_TIMESTAMP
                    })
                    
                    # ... (all other sensor/energy/safety updates are here) ...
                    
                    humid_val = get_slight_change(50.0, 30, 60, max_change=1.0)
                    db.collection('facilities').document(fid).collection('sensors').document('humid_01').set({
                        'sensor_type': 'Humidity', 'current_value': humid_val, 'unit': '%', 'last_updated': firestore.SERVER_TIMESTAMP
                    })
                    
                    vib_val = get_slight_change(0.1, 0.0, 0.5, max_change=0.05)
                    db.collection('facilities').document(fid).collection('sensors').document('vib_01').set({
                        'sensor_type': 'Vibration', 'current_value': vib_val, 'unit': 'Hz', 'last_updated': firestore.SERVER_TIMESTAMP
                    })

                    # --- B. Log Daily Energy (Sub-collection) ---
                    new_solar = round(random.uniform(800, 1600), 2)
                    new_grid = round(random.uniform(500, 1200), 2)
                    new_efficiency = round(new_solar / (new_solar + new_grid), 2)
                    
                    db.collection('facilities').document(fid).collection('energy_usage').document(today_str).set({
                        'solar_energy_kwh': new_solar, 'grid_energy_kwh': new_grid, 'energy_efficiency': new_efficiency
                    })

                    # --- C. Log Daily Safety & Update Main Doc ---
                    incidents = random.randint(0, 2)
                    faults = random.randint(0, 5) if 'dc' not in fid else 0
                    anomalies = random.randint(0, 3)
                    new_safety_score = calculate_ai_safety_score(incidents, faults, anomalies)

                    db.collection('facilities').document(fid).collection('safety_reports').document(today_str).set({
                        'incidents_last_month': incidents, 'automation_faults': faults, 'energy_anomalies': anomalies, 'ai_safety_score': new_safety_score
                    })
                    
                    db.collection('facilities').document(fid).update({'safety_score': new_safety_score})
                    
                    # --- D. Update Data Center Stats (if it is one) ---
                    if 'dc' in fid:
                        new_uptime = round(random.uniform(99.95, 99.99), 2)
                        new_clients = random.randint(45, 55)
                        db.collection('facilities').document(fid).update({
                            'uptime_percentage': new_uptime, 'clients_connected': new_clients
                        })
                    
                    print(f"    ✅ Successfully updated data for: {fid}")
                
                except Exception as e:
                    # If ONE facility fails, print the error and continue
                    print(f"    ❌ ERROR updating data for {fid}: {e}")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] --- Update cycle complete ---")
            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user.")

# --- Initialization (MODIFIED) ---
if __name__ == "__main__":
    try:
        # Use the key file to authenticate
        cred = credentials.Certificate('firebase-key.json')
        
        # *** NEW LINE ***
        # This explicitly tells the SDK which project to use.
        # This can solve "project not found" errors.
        firebase_admin.initialize_app(cred, {
            'projectId': 'prologiq-hub', 
        })
        
        db = firestore.client()
        print("✅ Firebase initialized successfully.")
        run_simulation(db)
        
    except FileNotFoundError:
        print("="*50)
        print("❌ ERROR: 'firebase-key.json' not found!")
        print("Please make sure your service account key is in the")
        print("same folder as this script and named correctly.")
        print("="*50)
    except Exception as e:
        # This will catch any other startup errors
        print(f"❌ An unexpected error occurred during initialization: {e}")