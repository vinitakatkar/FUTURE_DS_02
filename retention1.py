import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file_path = "C:/Users/matek/Desktop/futureintern/task2/customer_data1.xlsx"

output_folder = "C:/Users/matek/Desktop/futureintern/task2/retention_output"

os.makedirs(output_folder, exist_ok=True)

sns.set_theme(style="whitegrid")

try:
    df = pd.read_excel(file_path)
    print("Data loaded successfully!")

except Exception as e:
    print("Error loading Excel file:")
    print(e)
    exit()

df.columns = df.columns.str.strip()

required_columns = [
    "Customer_ID",
    "Signup_Date",
    "Plan",
    "Age",
    "Gender",
    "Region",
    "Monthly_Charges",
    "Tenure_Months",
    "Payment_Method",
    "Support_Calls",
    "Churn",
    "Churn_Reason",
    "Signup_Month"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    print("Missing columns:")
    print(missing_columns)
    exit()

print("\nOriginal records:", len(df))

df = df.drop_duplicates()

text_columns = [
    "Customer_ID",
    "Plan",
    "Gender",
    "Region",
    "Payment_Method",
    "Churn",
    "Churn_Reason"
]

for column in text_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )

df["Churn"] = df["Churn"].str.title()

df["Signup_Date"] = pd.to_datetime(
    df["Signup_Date"],
    errors="coerce"
)

numeric_columns = [
    "Age",
    "Monthly_Charges",
    "Tenure_Months",
    "Support_Calls"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

df = df.dropna(
    subset=[
        "Customer_ID",
        "Signup_Date",
        "Plan",
        "Monthly_Charges",
        "Tenure_Months",
        "Churn"
    ]
)

df["Signup_Month"] = (
    df["Signup_Date"]
    .dt.to_period("M")
    .astype(str)
)

print("Records after cleaning:", len(df))

total_customers = df["Customer_ID"].nunique()

churned_customers = df.loc[
    df["Churn"] == "Yes",
    "Customer_ID"
].nunique()

retained_customers = df.loc[
    df["Churn"] == "No",
    "Customer_ID"
].nunique()

churn_rate = (
    churned_customers /
    total_customers *
    100
)

retention_rate = (
    retained_customers /
    total_customers *
    100
)

average_tenure = df["Tenure_Months"].mean()

average_monthly_charge = df["Monthly_Charges"].mean()

total_monthly_revenue = df["Monthly_Charges"].sum()

estimated_clv = (
    average_monthly_charge *
    average_tenure
)

print("\nKEY PERFORMANCE INDICATORS")

print("Total Customers:", total_customers)
print("Churned Customers:", churned_customers)
print("Retained Customers:", retained_customers)
print("Churn Rate:", round(churn_rate, 2), "%")
print("Retention Rate:", round(retention_rate, 2), "%")
print("Average Tenure:", round(average_tenure, 2), "months")
print(
    "Average Monthly Charge:",
    round(average_monthly_charge, 2)
)
print(
    "Monthly Revenue:",
    round(total_monthly_revenue, 2)
)
print(
    "Estimated CLV:",
    round(estimated_clv, 2)
)

kpi_summary = pd.DataFrame({
    "Metric": [
        "Total Customers",
        "Churned Customers",
        "Retained Customers",
        "Churn Rate",
        "Retention Rate",
        "Average Tenure",
        "Average Monthly Charges",
        "Total Monthly Revenue",
        "Estimated Customer Lifetime Value"
    ],
    "Value": [
        total_customers,
        churned_customers,
        retained_customers,
        round(churn_rate, 2),
        round(retention_rate, 2),
        round(average_tenure, 2),
        round(average_monthly_charge, 2),
        round(total_monthly_revenue, 2),
        round(estimated_clv, 2)
    ]
})

plan_analysis = (
    df.groupby("Plan")
    .agg(
        Customers=("Customer_ID", "nunique"),
        Churned_Customers=(
            "Churn",
            lambda x: (x == "Yes").sum()
        ),
        Average_Charges=(
            "Monthly_Charges",
            "mean"
        ),
        Average_Tenure=(
            "Tenure_Months",
            "mean"
        )
    )
    .reset_index()
)

plan_analysis["Churn_Rate"] = (
    plan_analysis["Churned_Customers"] /
    plan_analysis["Customers"] *
    100
)

plan_analysis["Revenue"] = (
    df.groupby("Plan")["Monthly_Charges"]
    .sum()
    .values
)

region_analysis = (
    df.groupby("Region")
    .agg(
        Customers=("Customer_ID", "nunique"),
        Churned_Customers=(
            "Churn",
            lambda x: (x == "Yes").sum()
        ),
        Average_Charges=(
            "Monthly_Charges",
            "mean"
        ),
        Average_Tenure=(
            "Tenure_Months",
            "mean"
        )
    )
    .reset_index()
)

region_analysis["Churn_Rate"] = (
    region_analysis["Churned_Customers"] /
    region_analysis["Customers"] *
    100
)

payment_analysis = (
    df.groupby("Payment_Method")
    .agg(
        Customers=("Customer_ID", "nunique"),
        Churned_Customers=(
            "Churn",
            lambda x: (x == "Yes").sum()
        )
    )
    .reset_index()
)

payment_analysis["Churn_Rate"] = (
    payment_analysis["Churned_Customers"] /
    payment_analysis["Customers"] *
    100
)

support_analysis = (
    df.groupby("Churn")
    .agg(
        Customers=("Customer_ID", "nunique"),
        Average_Support_Calls=(
            "Support_Calls",
            "mean"
        ),
        Average_Tenure=(
            "Tenure_Months",
            "mean"
        ),
        Average_Charges=(
            "Monthly_Charges",
            "mean"
        )
    )
    .reset_index()
)

tenure_bins = [
    0,
    3,
    6,
    12,
    24,
    float("inf")
]

tenure_labels = [
    "0-3 Months",
    "4-6 Months",
    "7-12 Months",
    "13-24 Months",
    "25+ Months"
]

df["Tenure_Group"] = pd.cut(
    df["Tenure_Months"],
    bins=tenure_bins,
    labels=tenure_labels,
    include_lowest=True
)

tenure_analysis = (
    df.groupby("Tenure_Group", observed=True)
    .agg(
        Customers=("Customer_ID", "nunique"),
        Churned_Customers=(
            "Churn",
            lambda x: (x == "Yes").sum()
        ),
        Average_Charges=(
            "Monthly_Charges",
            "mean"
        )
    )
    .reset_index()
)

tenure_analysis["Churn_Rate"] = (
    tenure_analysis["Churned_Customers"] /
    tenure_analysis["Customers"] *
    100
)

churn_reasons = (
    df[df["Churn"] == "Yes"]
    ["Churn_Reason"]
    .dropna()
    .value_counts()
    .reset_index()
)

churn_reasons.columns = [
    "Churn_Reason",
    "Customers"
]

monthly_signups = (
    df.groupby("Signup_Month")
    ["Customer_ID"]
    .nunique()
    .reset_index()
)

monthly_signups.columns = [
    "Signup_Month",
    "New_Customers"
]

cohort_analysis = (
    df.groupby("Signup_Month")
    .agg(
        Customers=("Customer_ID", "nunique"),
        Churned_Customers=(
            "Churn",
            lambda x: (x == "Yes").sum()
        ),
        Average_Tenure=(
            "Tenure_Months",
            "mean"
        )
    )
    .reset_index()
)

cohort_analysis["Churn_Rate"] = (
    cohort_analysis["Churned_Customers"] /
    cohort_analysis["Customers"] *
    100
)

cohort_analysis["Retention_Rate"] = (
    100 -
    cohort_analysis["Churn_Rate"]
)

age_bins = [
    17,
    25,
    35,
    45,
    55,
    100
]

age_labels = [
    "18-25",
    "26-35",
    "36-45",
    "46-55",
    "56+"
]

df["Age_Group"] = pd.cut(
    df["Age"],
    bins=age_bins,
    labels=age_labels,
    include_lowest=True
)

age_analysis = (
    df.groupby("Age_Group", observed=True)
    .agg(
        Customers=("Customer_ID", "nunique"),
        Churned_Customers=(
            "Churn",
            lambda x: (x == "Yes").sum()
        )
    )
    .reset_index()
)

age_analysis["Churn_Rate"] = (
    age_analysis["Churned_Customers"] /
    age_analysis["Customers"] *
    100
)

plan_revenue = (
    df.groupby("Plan")
    ["Monthly_Charges"]
    .sum()
    .reset_index()
)

plan_revenue.columns = [
    "Plan",
    "Monthly_Revenue"
]

correlation = df[
    [
        "Age",
        "Monthly_Charges",
        "Tenure_Months",
        "Support_Calls"
    ]
].corr()

high_risk = df[
    (df["Churn"] == "Yes") &
    (df["Support_Calls"] >= 3)
].copy()

high_risk["Risk_Level"] = "High"

recommendations = pd.DataFrame({
    "Area": [
        "Customer Support",
        "Early Tenure",
        "Pricing",
        "Payment Methods",
        "Churn Reasons"
    ],
    "Recommendation": [
        "Identify customers with frequent support calls and provide proactive assistance.",
        "Create onboarding and engagement campaigns for customers in their first 6 months.",
        "Review pricing and value perception for plans with above-average churn.",
        "Investigate payment methods associated with higher churn.",
        "Prioritize the most common churn reasons for retention initiatives."
    ]
})

plt.figure(figsize=(8, 5))

plan_analysis.plot(
    x="Plan",
    y="Churn_Rate",
    kind="bar",
    legend=False
)

plt.title("Churn Rate by Subscription Plan")
plt.xlabel("Plan")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "01_Churn_by_Plan.png"
    ),
    dpi=300
)

plt.show()
plt.close()

plt.figure(figsize=(8, 5))

region_analysis.plot(
    x="Region",
    y="Churn_Rate",
    kind="bar",
    legend=False
)

plt.title("Churn Rate by Region")
plt.xlabel("Region")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "02_Churn_by_Region.png"
    ),
    dpi=300
)

plt.show()
plt.close()

plt.figure(figsize=(9, 5))

tenure_analysis.plot(
    x="Tenure_Group",
    y="Churn_Rate",
    kind="bar",
    legend=False
)

plt.title("Churn Rate by Customer Tenure")
plt.xlabel("Tenure Group")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "03_Churn_by_Tenure.png"
    ),
    dpi=300
)

plt.show()
plt.close()

plt.figure(figsize=(9, 5))

churn_reasons.head(10).plot(
    x="Churn_Reason",
    y="Customers",
    kind="bar",
    legend=False
)

plt.title("Top Churn Reasons")
plt.xlabel("Churn Reason")
plt.ylabel("Customers")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "04_Churn_Reasons.png"
    ),
    dpi=300
)

plt.show()
plt.close()

plt.figure(figsize=(9, 5))

payment_analysis.plot(
    x="Payment_Method",
    y="Churn_Rate",
    kind="bar",
    legend=False
)

plt.title("Churn Rate by Payment Method")
plt.xlabel("Payment Method")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "05_Churn_by_Payment.png"
    ),
    dpi=300
)

plt.show()
plt.close()

plt.figure(figsize=(8, 5))

support_analysis.plot(
    x="Churn",
    y="Average_Support_Calls",
    kind="bar",
    legend=False
)

plt.title("Average Support Calls by Churn Status")
plt.xlabel("Churn Status")
plt.ylabel("Average Support Calls")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "06_Support_Calls_vs_Churn.png"
    ),
    dpi=300
)

plt.show()
plt.close()

plt.figure(figsize=(10, 5))

monthly_signups.plot(
    x="Signup_Month",
    y="New_Customers",
    kind="line",
    marker="o",
    legend=False
)

plt.title("Monthly Customer Signups")
plt.xlabel("Signup Month")
plt.ylabel("New Customers")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "07_Monthly_Signups.png"
    ),
    dpi=300
)

plt.show()
plt.close()

plt.figure(figsize=(8, 5))

age_analysis.plot(
    x="Age_Group",
    y="Churn_Rate",
    kind="bar",
    legend=False
)

plt.title("Churn Rate by Age Group")
plt.xlabel("Age Group")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "08_Churn_by_Age.png"
    ),
    dpi=300
)

plt.show()
plt.close()

plt.figure(figsize=(8, 6))

sns.heatmap(
    correlation,
    annot=True,
    fmt=".2f"
)

plt.title("Customer Data Correlation")

plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "09_Correlation_Heatmap.png"
    ),
    dpi=300
)

plt.show()
plt.close()

report_file = os.path.join(
    output_folder,
    "Customer_Retention_Report1.xlsx"
)

with pd.ExcelWriter(
    report_file,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Cleaned_Data",
        index=False
    )

    kpi_summary.to_excel(
        writer,
        sheet_name="KPI_Summary",
        index=False
    )

    plan_analysis.to_excel(
        writer,
        sheet_name="Plan_Analysis",
        index=False
    )

    region_analysis.to_excel(
        writer,
        sheet_name="Region_Analysis",
        index=False
    )

    payment_analysis.to_excel(
        writer,
        sheet_name="Payment_Analysis",
        index=False
    )

    support_analysis.to_excel(
        writer,
        sheet_name="Support_Analysis",
        index=False
    )

    tenure_analysis.to_excel(
        writer,
        sheet_name="Tenure_Analysis",
        index=False
    )

    churn_reasons.to_excel(
        writer,
        sheet_name="Churn_Reasons",
        index=False
    )

    monthly_signups.to_excel(
        writer,
        sheet_name="Monthly_Signups",
        index=False
    )

    cohort_analysis.to_excel(
        writer,
        sheet_name="Cohort_Analysis",
        index=False
    )

    age_analysis.to_excel(
        writer,
        sheet_name="Age_Analysis",
        index=False
    )

    plan_revenue.to_excel(
        writer,
        sheet_name="Plan_Revenue",
        index=False
    )

    correlation.to_excel(
        writer,
        sheet_name="Correlation"
    )

    high_risk.to_excel(
        writer,
        sheet_name="High_Risk_Customers",
        index=False
    )

    recommendations.to_excel(
        writer,
        sheet_name="Recommendations",
        index=False
    )

print("\n")
print("=" * 65)
print("CUSTOMER RETENTION ANALYSIS COMPLETED")
print("=" * 65)

print("\nTotal Customers:", total_customers)
print("Churned Customers:", churned_customers)
print("Retained Customers:", retained_customers)
print("Churn Rate:", round(churn_rate, 2), "%")
print("Retention Rate:", round(retention_rate, 2), "%")
print("Average Tenure:", round(average_tenure, 2), "months")
print(
    "Average Monthly Charges:",
    round(average_monthly_charge, 2)
)
print(
    "Total Monthly Revenue:",
    round(total_monthly_revenue, 2)
)
print(
    "Estimated CLV:",
    round(estimated_clv, 2)
)

print("\nExcel report:")
print(report_file)

print("\nCharts saved in:")
print(output_folder)

print("\nProject completed successfully!")
