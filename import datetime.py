import datetime

# =============================================
# TASK 1 SIMULATION: Data Redundancy Removal System
# (Simulating a Write Gatekeeper Service)
# =============================================
# This script demonstrates the logic flow: Validate -> Check Duplicates -> Insert.

# -----------------------
# 1. SIMULATED DATABASE
# -----------------------
simulated_database = []

# --- Type Hinting / Documentation ---
# In Python, we use docstrings and type hints for clarity.
# DataRecord structure: transactionId (str), userId (str), amount (float), timestamp (datetime.date), locationCode (str)


def initialize_database():
    """Initializes the database with some sample, non-duplicate data."""
    print("--- [SYSTEM INITIALIZATION] ---")
    # Using current time and a slightly older time for simulation
    initial_data = [
        {
            "transactionId": "TX1001", 
            "userId": "U456", 
            "amount": 99.99, 
            "timestamp": datetime.datetime.now(), 
            "locationCode": "NYC"
        },
        {
            "transactionId": "TX1002", 
            "userId": "U789", 
            "amount": 25.50, 
            "timestamp": datetime.datetime.now() - datetime.timedelta(hours=1), # One hour ago
            "locationCode": "LAX"
        }
    ]
    for record in initial_data:
        simulated_database.append(record)
    print(f"✅ Database initialized with {len(simulated_database)} existing records.")

# -----------------------
# 2. CORE VALIDATION & CHECKING FUNCTIONS
# -----------------------

def validate_schema(data: dict) -> dict:
    """Performs Schema and Business Rule Validation on the incoming data payload."""
    print("\n--- [STEP 1: SCHEMA VALIDATION] ---")

    # Check for mandatory fields and correct types (Business Logic Example)
    if not isinstance(data.get("transactionId"), str) or not data["transactionId"]:
        return {"isValid": False, "message": "Validation Failed: Missing or invalid 'transactionId'."}
    
    valid_locations = ["NYC", "LAX", "CHI"]
    if data.get("locationCode") not in valid_locations:
        return {"isValid": False, "message": f"Validation Failed: Invalid location code '{data['locationCode']}'. Must be {', '.join(valid_locations)}."}
    
    amount = data.get("amount")
    if not isinstance(amount, (int, float)) or amount <= 0:
        return {"isValid": False, "message": "Validation Failed: Amount must be a positive number."}

    return {"isValid": True, "message": "Schema validation passed."}


def check_for_redundancy(new_data: dict) -> dict:
    """Checks the incoming record against all existing records in the simulated DB."""
    print("\n--- [STEP 2: REDUNDANCY CHECK] ---")

    # Check for exact duplicate Transaction ID (Primary Key check)
    is_exact_duplicate = any(record["transactionId"] == new_data["transactionId"] for record in simulated_database)

    if is_exact_duplicate:
        return {"isDuplicate": True, "reason": f"Hard Duplicate detected by Transaction ID ({new_data['transactionId']})."}

    # Advanced Redundancy Check Example (Simulated): Checking for near-duplicates based on location/user group.
    potential_match = next((
        record for record in simulated_database 
        if record["userId"] == new_data["userId"] and 
           record["locationCode"] == new_data["locationCode"] and
           abs(record["amount"] - new_data["amount"]) < 0.01 # Tolerance for small float differences
    ), None)

    if potential_match:
         return {"isDuplicate": True, "reason": f"Potential near-duplicate found with existing record {potential_match['transactionId']}. Data may already exist."}


    return {"isDuplicate": False, "reason": "No redundancy detected."}


# -----------------------
# 3. MAIN GATEKEEPER SERVICE (The Transaction Manager)
# -----------------------

def process_new_entry(incoming_data: dict) -> dict:
    """
    The main function that processes incoming data through the entire pipeline,
    simulating a database transaction block.
    """
    print("\n" + "="*60)
    print(f"🚀 Processing NEW ENTRY for Transaction ID: {incoming_data['transactionId']}")
    print("="*60)

    # 1. Validation Check (Schema & Business Rules)
    validation_result = validate_schema(incoming_data)
    if not validation_result["isValid"]:
        return {"success": False, "message": f"🛑 REJECTION at Validation Stage: {validation_result['message']}"}
    print(f"✅ Validation Passed: {validation_result['message']}")

    # 2. Redundancy Check (Against existing data)
    redundancy_check = check_for_redundancy(incoming_data)
    if redundancy_check["isDuplicate"]:
        return {"success": False, "message": f"🛑 REJECTION at Redundancy Stage: {redundancy_check['reason']}"}
    print(f"✅ Redundancy Check Passed: {redundancy_check['reason']}")

    # 3. Transaction Commit (If all checks pass)
    try:
        new_record = {
            "transactionId": incoming_data["transactionId"],
            "userId": incoming_data["userId"],
            "amount": float(incoming_data["amount"]),
            "timestamp": datetime.datetime.now(), # Use actual system time for insertion timestamp
            "locationCode": incoming_data["locationCode"]
        }

        # *** THIS IS THE COMMIT STEP ***
        simulated_database.append(new_record) 
        print("\n✨ TRANSACTION SUCCESS: Data committed successfully to the cloud database!")
        return {"success": True, "message": f"Successfully added unique record {incoming_data['transactionId']}."}

    except Exception as e:
        # In a real system, this would trigger ROLLBACK automatically
        print(f"🚨 CRITICAL ERROR during commit: {e}")
        return {"success": False, "message": "🛑 SYSTEM FAILURE: Failed to write data due to an unexpected database error."}


# -----------------------
# --- EXECUTION & TESTING ---
# -----------------------

initialize_database()

# --- Test Case 1: Successful, Unique Entry (Should Pass) ---
successful_data = {
    "transactionId": "TX9003", 
    "userId": "U123", 
    "amount": 55.75, 
    "locationCode": "CHI"
}
result1 = process_new_entry(successful_data)
print(">>> RESULT 1:", result1['message'])

# --- Test Case 2: Duplicate Entry (Should Fail at Redundancy Check) ---
duplicate_data = {
    "transactionId": "TX1001", # This ID already exists from initialization
    "userId": "U999", 
    "amount": 50.00, 
    "locationCode": "CHI"
}
result2 = process_new_entry(duplicate_data)
print("\n>>> RESULT 2:", result2['message'])


# --- Test Case 3: Schema Failure (Invalid Location Code) (Should Fail at Validation Step) ---
invalid_schema_data = {
    "transactionId": "TX9004", 
    "userId": "U123", 
    "amount": 10.00, 
    "locationCode": "XYZ" # Invalid code
}
result3 = process_new_entry(invalid_schema_data)
print("\n>>> RESULT 3:", result3['message'])


# --- Test Case 4: Validation Failure (Bad Amount) (Should Fail at Validation Step) ---
invalid_amount_data = {
    "transactionId": "TX9005", 
    "userId": "U123", 
    "amount": -5.00, # Negative amount
    "locationCode": "NYC"
}
result4 = process_new_entry(invalid_amount_data)
print("\n>>> RESULT 4:", result4['message'])


# Final check to see the resulting database content size
print("\n=========================================")
print(f"FINAL DATABASE SIZE: {len(simulated_database)} records.")
print("The system successfully filtered out attempts and retained only valid, unique data.")
