import os
import json

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def generate_chart(data: dict, output_dir: str = "outputs") -> str:
    """Generate a status distribution pie chart from findings data.
    Returns the file path of the generated chart image.
    """
    if not HAS_MATPLOTLIB:
        return ""
    
    os.makedirs(output_dir, exist_ok=True)
    
    approved = 0
    review = 0
    rejected = 0
    
    for item in data.get("findings", []):
        status = item.get("status", "")
        if status == "Approved":
            approved += 1
        elif status == "Review":
            review += 1
        elif status == "Rejected":
            rejected += 1
    
    labels = ["Approved", "Review", "Rejected"]
    sizes = [approved, review, rejected]
    
    # Filter out zero values
    filtered = [(l, s) for l, s in zip(labels, sizes) if s > 0]
    if not filtered:
        return ""
    
    labels, sizes = zip(*filtered)
    
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%")
    plt.title(data.get("title", "Status Distribution"))
    
    chart_path = os.path.join(output_dir, "approval_chart.png")
    plt.savefig(chart_path)
    plt.close()
    
    return chart_path


if __name__ == "__main__":
    with open("data.json", "r") as f:
        data = json.load(f)
    path = generate_chart(data, "output")
    print(f"Chart Generated: {path}")