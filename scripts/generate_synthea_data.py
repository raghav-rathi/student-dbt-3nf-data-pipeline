import csv
import os
import random
import uuid
from datetime import datetime, timedelta

def generate_synthea_dataset(output_dir, num_patients=50):
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42)

    # 1. ORGANIZATIONS
    org_names = [
        "Massachusetts General Hospital", "Brigham and Women's Hospital",
        "Beth Israel Deaconess Medical Center", "Boston Medical Center",
        "Tufts Medical Center", "Cambridge Health Alliance", "St. Elizabeth's Medical Center"
    ]
    organizations = []
    for i, name in enumerate(org_names):
        org_id = f"ORG-{100 + i}"
        organizations.append({
            "id": org_id,
            "name": name,
            "address": f"{100 + i * 5} Main St",
            "city": "Boston",
            "state": "MA",
            "zip": f"021{10 + i}",
            "phone": f"617-555-01{i:02d}",
            "revenue": round(random.uniform(5000000, 25000000), 2)
        })

    # 2. PAYORS
    payor_names = [
        "Medicare", "Medicaid", "Blue Cross Blue Shield",
        "Aetna", "UnitedHealthcare", "Cigna", "Humana"
    ]
    payors = []
    for i, name in enumerate(payor_names):
        payor_id = f"PAYOR-{200 + i}"
        payors.append({
            "id": payor_id,
            "name": name,
            "address": f"{200 + i * 3} Commercial St",
            "city": "Boston",
            "state": "MA",
            "zip": f"021{20 + i}",
            "phone": f"800-555-02{i:02d}"
        })

    # 3. PROVIDERS
    specialties = ["General Practice", "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Pulmonology", "Dermatology"]
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    providers = []
    for i in range(15):
        provider_id = f"DR-{300 + i}"
        org = random.choice(organizations)
        providers.append({
            "id": provider_id,
            "organization": org["id"],
            "name": f"Dr. {random.choice(first_names)} {random.choice(last_names)}",
            "gender": random.choice(["M", "F"]),
            "speciality": random.choice(specialties),
            "address": org["address"],
            "city": org["city"],
            "state": org["state"],
            "zip": org["zip"]
        })

    # 4. PATIENTS
    patients = []
    for i in range(num_patients):
        patient_id = f"PAT-{1000 + i}"
        birth_year = random.randint(1950, 2010)
        birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
        patients.append({
            "id": patient_id,
            "birthdate": birth_date.strftime("%Y-%m-%d"),
            "deathdate": "",
            "ssn": f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",
            "first": random.choice(first_names),
            "last": random.choice(last_names),
            "gender": random.choice(["M", "F"]),
            "race": random.choice(["White", "Black", "Asian", "Hispanic"]),
            "ethnicity": "Non-Hispanic",
            "address": f"{random.randint(1, 999)} Beacon St",
            "city": "Boston",
            "state": "MA",
            "zip": "02115",
            "insurance_provider": random.choice(payors)["name"],
            "updated_at": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S")
        })

    # 5. ENCOUNTERS, CONDITIONS, MEDICATIONS, PROCEDURES, CLAIMS
    encounter_classes = ["ambulatory", "emergency", "inpatient", "wellness", "urgentcare"]
    conditions_list = [
        ("44054006", "Diabetes mellitus type 2"),
        ("38341003", "Essential hypertension"),
        ("195662009", "Acute bronchitis"),
        ("233604007", "Pneumonia"),
        ("10509000", "Acute sinusitis"),
        ("40055000", "Chronic obstructive pulmonary disease")
    ]
    medications_list = [
        ("310800", "Metformin 500 MG Oral Tablet"),
        ("197361", "Amlodipine 5 MG Oral Tablet"),
        ("1191", "Aspirin 81 MG Oral Tablet"),
        ("314422", "Lisinopril 10 MG Oral Tablet"),
        ("861007", "Albuterol 90 MCG/ACTUATED Inhaler")
    ]
    procedures_list = [
        ("18286008", "Chest X-ray"),
        ("4397009", "Electrocardiogram"),
        ("274025005", "Blood chemistry test"),
        ("104001", "Standard physical examination")
    ]

    encounters = []
    conditions = []
    medications = []
    procedures = []
    claims = []

    start_base = datetime(2024, 1, 1)

    for i in range(120):
        encounter_id = f"ENC-{5000 + i}"
        patient = random.choice(patients)
        provider = random.choice(providers)
        payor = random.choice(payors)
        
        start_dt = start_base + timedelta(days=random.randint(0, 180), hours=random.randint(0, 23))
        duration_hours = random.choice([1, 2, 4, 12, 24, 48, 72])
        stop_dt = start_dt + timedelta(hours=duration_hours)

        enc_class = random.choice(encounter_classes)
        base_cost = round(random.uniform(150, 3500), 2)
        payer_cov = round(base_cost * random.uniform(0.6, 0.95), 2)

        encounters.append({
            "id": encounter_id,
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stop": stop_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "patient": patient["id"],
            "organization": provider["organization"],
            "provider": provider["id"],
            "payor": payor["id"],
            "encounterclass": enc_class,
            "code": "185345009",
            "description": f"{enc_class.capitalize()} Encounter",
            "base_encounter_cost": base_cost,
            "total_claim_cost": base_cost,
            "payer_coverage": payer_cov,
            "reasoncode": "44054006",
            "reasondescription": "Routine Checkup / Care"
        })

        # Condition for encounter
        cond_code, cond_desc = random.choice(conditions_list)
        conditions.append({
            "start": start_dt.strftime("%Y-%m-%d"),
            "stop": stop_dt.strftime("%Y-%m-%d"),
            "patient": patient["id"],
            "encounter": encounter_id,
            "code": cond_code,
            "description": cond_desc
        })

        # Medication for encounter
        med_code, med_desc = random.choice(medications_list)
        med_cost = round(random.uniform(20, 150), 2)
        medications.append({
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stop": stop_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "patient": patient["id"],
            "encounter": encounter_id,
            "code": med_code,
            "description": med_desc,
            "base_cost": med_cost,
            "payer_coverage": round(med_cost * 0.8, 2),
            "dispenses": random.randint(1, 3),
            "totalcost": med_cost
        })

        # Procedure
        proc_code, proc_desc = random.choice(procedures_list)
        proc_cost = round(random.uniform(100, 800), 2)
        procedures.append({
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stop": stop_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "patient": patient["id"],
            "encounter": encounter_id,
            "code": proc_code,
            "description": proc_desc,
            "base_cost": proc_cost
        })

        # Claim
        claims.append({
            "id": f"CLM-{7000 + i}",
            "patient": patient["id"],
            "provider": provider["id"],
            "status": random.choice(["closed", "closed", "open"]),
            "outstandingdate": start_dt.strftime("%Y-%m-%d"),
            "servicedate": start_dt.strftime("%Y-%m-%d")
        })

    # Write CSV files
    def write_csv(filename, data, fieldnames):
        path = os.path.join(output_dir, filename)
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"  [+] Generated {filename}: {len(data)} rows")

    write_csv("organizations.csv", organizations, ["id", "name", "address", "city", "state", "zip", "phone", "revenue"])
    write_csv("payors.csv", payors, ["id", "name", "address", "city", "state", "zip", "phone"])
    write_csv("providers.csv", providers, ["id", "organization", "name", "gender", "speciality", "address", "city", "state", "zip"])
    write_csv("patients.csv", patients, ["id", "birthdate", "deathdate", "ssn", "first", "last", "gender", "race", "ethnicity", "address", "city", "state", "zip", "insurance_provider", "updated_at"])
    write_csv("encounters.csv", encounters, ["id", "start", "stop", "patient", "organization", "provider", "payor", "encounterclass", "code", "description", "base_encounter_cost", "total_claim_cost", "payer_coverage", "reasoncode", "reasondescription"])
    write_csv("conditions.csv", conditions, ["start", "stop", "patient", "encounter", "code", "description"])
    write_csv("medications.csv", medications, ["start", "stop", "patient", "encounter", "code", "description", "base_cost", "payer_coverage", "dispenses", "totalcost"])
    write_csv("procedures.csv", procedures, ["start", "stop", "patient", "encounter", "code", "description", "base_cost"])
    write_csv("claims.csv", claims, ["id", "patient", "provider", "status", "outstandingdate", "servicedate"])

if __name__ == "__main__":
    generate_synthea_dataset("data/synthea_raw")
