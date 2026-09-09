import json

company = input("Company: ")
reviewer = input("Reviewer: ")
department = input("Department: ")

findings = []

count = int(input("Number of findings: "))

for i in range(count):

    print(f"\nFinding {i+1}")

    field = input("Field: ")
    value = input("Value: ")
    status = input("Status: ")

    findings.append(
        {
            "field": field,
            "value": value,
            "status": status
        }
    )

recommendations = []

rec_count = int(
    input("Number of recommendations: ")
)

for i in range(rec_count):

    recommendations.append(
        input(
            f"Recommendation {i+1}: "
        )
    )

data = {
    "title": f"{company} Approval Note",
    "company": company,
    "reviewer": reviewer,
    "department": department,
    "findings": findings,
    "recommendations": recommendations
}

with open(
    "data.json",
    "w"
) as file:

    json.dump(
        data,
        file,
        indent=4
    )

print("\nJSON Generated Successfully!")