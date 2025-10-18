import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date

def seed_database():
    try:
        # --- 1. Connect to Firebase ---
        # (This assumes you already have an app initialized)
        # If you run this separately, you'll need the init code
        try:
            db = firestore.client()
        except ValueError:
            print("Connecting to Firebase...")
            cred = credentials.Certificate('firebase-key.json')
            firebase_admin.initialize_app(cred, {'projectId': 'prologiq-hub'})
            db = firestore.client()
        
        print("✅ Firebase connected. Seeding database...")

        facility_ids = [
            'facility_sfo_01', 
            'facility_dal_02', 
            'facility_atl_03', 
            'facility_sea_04_dc'
        ]

        for fid in facility_ids:
            print(f"  > Seeding data for: {fid}")
            
            # --- 2. Seed INVENTORY Data ---
            # Get the sub-collection for inventory
            inventory_ref = db.collection('facilities').document(fid).collection('inventory')
            
            # Add some sample inventory items
            inventory_ref.add({
                'item_name': 'Automated Guided Vehicle (AGV)',
                'quantity': 12,
                'category': 'Robotics',
                'reorder_threshold': 5
            })
            
            inventory_ref.add({
                'item_name': 'Conveyor Belt Motor',
                'quantity': 45,
                'category': 'Spare Parts',
                'reorder_threshold': 20
            })
            
            inventory_ref.add({
                'item_name': 'Server Rack (42U)',
                'quantity': 8,
                'category': 'Data Center Hardware',
                'reorder_threshold': 10
            })
            
            # --- 3. Seed MAINTENANCE LOGS ---
            logs_ref = db.collection('facilities').document(fid).collection('maintenance_logs')
            
            logs_ref.add({
                'performed_by': 'Facility Tech Team',
                'action_taken': 'Replaced air filter on HVAC Unit #3.',
                'maintenance_date': date(2025, 9, 15).isoformat(),
                'cost': 450.00
            })
            
            logs_ref.add({
                'performed_by': 'Robotics Inc.',
                'action_taken': 'Calibrated AGV guidance system.',
                'maintenance_date': date(2025, 10, 1).isoformat(),
                'cost': 1200.00
            })

        print("\n🎉 Database seeding complete!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

# --- Run the script ---
if __name__ == "__main__":
    seed_database()