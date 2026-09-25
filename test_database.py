from data_manager import add_report, load_reports


test_report = {
    "report_id": "R001",
    "report_type": "found",
    "item_category": "water bottle",
    "colour": "black",
    "brand": "Hydro Flask",
    "material": "metal",
    "description": "Black water bottle with white logo",
    "location": "library",
    "date": "2026-09-25",
    "distinctive_features": ["white logo"],
    "status": "active"
}


result = add_report(test_report)

print("Saved:", result)
print("Reports:", load_reports())