import os
import win32com.client

def update_document():
    # Paths
    base_dir = os.path.abspath(r"C:\Users\jerma\Documents\Github\kq-sales-order-intelligence\docs")
    source_doc = os.path.join(base_dir, "JermaineObed_166588_Proposal.docx")
    target_doc = os.path.join(base_dir, "JermaineObed_166588_Proposal_Revised.docx")
    
    # Create COM object
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    
    try:
        # Open document
        doc = word.Documents.Open(source_doc)
        
        # 1. Update Title
        # We find the title string and replace it.
        # Let's just find "A Machine Learning-Driven Sales and Order Intelligence System for Kenya Airways' Water Production Unit (CAPSTONE)"
        # Or just find the first paragraph and change its text
        doc.Paragraphs(1).Range.Text = "An Integrated Web-Based Sales and Order Management System with Predictive Machine Learning Intelligence: A Case Study of Kenya Airways' Water Bottling Plant\n"
        
        # 2. Find "1.1 Background" and replace the text.
        # It's easier to find the heading, select the range from there to "1.2 Problem Statement", delete it, and insert new text.
        
        def replace_section(start_heading, end_heading, new_text):
            start_range = doc.Content
            if not start_range.Find.Execute(start_heading):
                return False
            
            end_range = doc.Content
            if not end_range.Find.Execute(end_heading):
                return False
            
            # Create a range from end of start_heading to beginning of end_heading
            replace_range = doc.Range(start_range.End, end_range.Start)
            replace_range.Text = "\n" + new_text + "\n"
            return True
            
        bg_text = """Kenya Airways (KQ), the flag carrier of Kenya, is one of Africa's leading airlines, operating a vast network of domestic, regional, and intercontinental routes from its hub at Jomo Kenyatta International Airport in Nairobi. Founded in 1977, the airline has grown to serve over 50 destinations, carrying millions of passengers annually. Beyond passenger travel, Kenya Airways manages a complex portfolio of ancillary and operational supply chain services. A critical component of this is the onboard water production and distribution function, which ensures the safe, compliant, and uninterrupted delivery of catering and cabin services across all flights.

In October 2024, as part of Project Kifaru (the airline's strategic recovery plan), Kenya Airways officially expanded its internal Water Bottling Plant. With a production capacity of approximately 4,500 litres per day, the plant was designed not only to reduce the airline's reliance on external water suppliers but also to generate independent revenue through bulk water sales to internal KQ departments, catering units, and external corporate clients (Kenya Airways, 2024).

However, the rapid expansion of this production capability has outpaced the administrative and technological infrastructure required to manage it. Currently, Kenya Airways' water sales and order operations are administered through highly fragmented, manual processes. Sales agents rely on paper-based ledgers to capture bulk orders; warehouse staff use standalone spreadsheets to track inventory; and finance teams rely on disconnected manual stock count sheets to generate billing.

This technological deficit creates significant operational friction. The reliance on manual data entry across isolated systems leads to persistent data silos, making real-time visibility into stock levels impossible. Consequently, warehouse officers frequently face stock discrepancies where physical inventory does not match ledger records. Furthermore, the absence of an integrated workflow introduces severe financial risks, including revenue leakage (where orders are dispatched but manually forgotten during the invoicing stage) and delayed billing cycles.

Beyond operational inefficiencies, management is severely handicapped by a lack of predictive intelligence. Without a centralised database of historical customer orders, sales trends cannot be analysed, and future water demand cannot be forecasted. Decisions regarding production planning and inventory stocking are currently made reactively rather than proactively.

Therefore, there is an urgent and critical need to transition from these fragmented, manual processes to an integrated, data-driven system. By implementing a centralised web-based sales and order management platform—augmented with machine learning algorithms capable of forecasting demand, segmenting customer buying behaviours, and flagging anomalous orders—Kenya Airways can eliminate revenue leakage, optimise inventory, and transform raw transactional data into actionable business intelligence.
"""
        replace_section("1.1\tBackground", "1.2\tProblem Statement", bg_text)
        
        # 3. Insert 1.6 Expected Outcomes before Chapter Two
        expected_outcomes = """
1.6\tExpected Project Outcomes
Upon completion, this project will deliver a fully functional, integrated software system alongside specific machine learning intelligence outputs. The tangible outcomes include:

1. Integrated Web-Based Platform: A deployed, role-based web application providing distinct, secure interfaces for Sales Agents, Warehouse Officers, Operations Managers, and System Administrators.
2. Automated Order-to-Cash Workflow: A functional pipeline that automatically decrements inventory upon order fulfilment and instantly generates downloadable PDF invoices, eliminating manual reconciliation.
3. Machine Learning Outputs:
   - Demand Forecasting Output: A predictive dashboard powered by a Time-Series Regression (SARIMAX) model that outputs the forecasted water order volume (in litres) expected over the next 30 days per customer segment.
   - Anomaly Detection Output: Real-time system alerts triggered by an Isolation Forest algorithm that flags specific incoming orders as "Suspicious" if they deviate significantly from historical patterns (e.g., an unusually massive bulk order from a historically dormant client).
   - Sales Trend & Segmentation Output: A visual clustering report generated by a K-Means algorithm that automatically categorises clients into segments (e.g., High-Value, At-Risk, Dormant) based on Recency, Frequency, and Monetary (RFM) metrics.
"""
        # Find Chapter Two
        ch2_range = doc.Content
        if ch2_range.Find.Execute("Chapter Two: Literature Review"):
            # Insert before Chapter Two
            ins_range = doc.Range(ch2_range.Start - 1, ch2_range.Start - 1)
            ins_range.Text = expected_outcomes + "\n"

        # 4. Insert 2.2 Theoretical Framework
        theoretical_framework = """
2.2\tTheoretical Framework
To ground the proposed system in established academic theory, this research adopts two foundational frameworks: the DeLone and McLean Information Systems Success Model (ISSM) and the Task-Technology Fit (TTF) Theory.

2.2.1 DeLone and McLean Information Systems Success Model (ISSM)
The DeLone and McLean (2003) ISSM posits that the success of an information system is evaluated across six dimensions: System Quality, Information Quality, Service Quality, Use, User Satisfaction, and Net Benefits. In the context of Kenya Airways' water operations, the current fragmented manual ledgers suffer from poor Information Quality (inaccurate stock data) and poor System Quality (disconnected spreadsheets). The proposed centralised web-based system directly targets these dimensions. By automating the data flow between order capture, stock deduction, and invoicing, the system enhances Information Quality (ensuring data integrity and real-time visibility) and System Quality (providing a unified, reliable platform). This theoretical basis justifies the core operational modules of the proposed system.

2.2.2 Task-Technology Fit (TTF) Theory
Goodhue and Thompson's (1995) Task-Technology Fit theory asserts that information technology is only likely to have a positive impact on individual performance if the capabilities of the technology closely match the tasks the user must perform. For the Operations Managers at Kenya Airways, their primary "task" is proactive decision-making regarding inventory allocation and revenue optimisation. Traditional CRUD (Create, Read, Update, Delete) systems fail to fit this task, as they only provide historical data. The introduction of Machine Learning models (the "technology")—specifically SARIMAX for forecasting, Isolation Forest for anomaly detection, and K-Means for customer segmentation—provides the exact predictive intelligence required to fit the manager's task. The TTF theory therefore justifies the inclusion and necessity of the machine learning intelligence layer within the system architecture.

"""
        # Find 2.2 Information Systems Integration and replace its heading or insert before it
        # The document currently has "2.2\tInformation Systems Integration and Sales Order Management"
        is_range = doc.Content
        if is_range.Find.Execute("2.2\tInformation Systems Integration and Sales Order Management"):
            # Insert the theoretical framework before this. We will have to renumber 2.2 to 2.3 manually or let Word auto-number if it's using lists
            # We'll just insert the text.
            ins_range = doc.Range(is_range.Start, is_range.Start)
            ins_range.Text = theoretical_framework
            
        # 5. Revise 2.6 Conceptual Framework
        # Add the explicit models paragraph
        cf_range = doc.Content
        if cf_range.Find.Execute("2.6\tConceptual Framework"):
            # Find the end of this section (Chapter Three)
            ch3_range = doc.Content
            ch3_range.Find.Execute("Chapter Three: Development Methodology")
            
            # Append this text to the end of 2.6
            append_range = doc.Range(ch3_range.Start - 1, ch3_range.Start - 1)
            append_text = "\n\nThe fifth layer, the Machine Learning Intelligence pipeline, acts as the predictive engine of the system. Rather than being a black box, it is explicitly defined by three distinct algorithmic flows. First, the SARIMAX algorithm ingests historical time-series order data to output 30-day demand forecasts. Second, the Isolation Forest algorithm evaluates incoming real-time transactions against historical baselines to output binary anomaly alerts (Normal/Suspicious) for fraud and error prevention. Third, the K-Means algorithm processes aggregated customer transaction histories through an RFM (Recency, Frequency, Monetary) matrix to output distinct customer behavioural segments. These distinct outputs are then passed to the Outputs layer, transforming raw data into actionable dashboards for Operations Managers.\n"
            append_range.Text = append_text

        # 6. Revise 3.2.3 Model Training
        model_training = """
The machine learning components of the proposed system will be trained entirely on bounded B2B sales and order transactional data captured within the system. The scope of this data is strictly limited to bulk water orders placed by internal KQ departments and external corporate clients, excluding B2C retail sales. Three specific models will be developed, trained, and integrated into the workflow:

1. Sales Demand Forecasting (Algorithm: SARIMAX)
Objective: To predict future bulk water order volumes, allowing warehouse staff to anticipate demand before stock depletion.
Algorithm: Seasonal Auto-Regressive Integrated Moving Average with eXogenous factors (SARIMAX). This algorithm is selected for its ability to handle time-series data with seasonal trends (e.g., increased water demand during specific operational seasons).
Inputs: Historical order dates, aggregated daily order quantities (in litres), and customer account categories.
Output: A time-series forecast displaying predicted order volumes for the upcoming 30-day window, surfaced on the Operations Manager's dashboard.

2. Order Anomaly Detection (Algorithm: Isolation Forest)
Objective: To automatically flag suspicious or highly irregular orders in real-time to prevent fraud, data entry errors, or supply chain shocks.
Algorithm: Isolation Forest. This unsupervised learning algorithm is highly effective for high-dimensional transactional datasets, as it isolates anomalies by randomly partitioning data rather than profiling normal behaviour.
Inputs: Real-time incoming order attributes, including requested quantity, order frequency relative to the specific customer's history, and unit price.
Output: A binary classification ("Normal" or "Anomalous"). If flagged as anomalous, the system generates an immediate alert requiring managerial approval before the order can proceed to warehouse fulfilment.

3. Customer Sales Trend Analysis (Algorithm: K-Means Clustering)
Objective: To segment corporate clients and internal departments based on their purchasing behaviours to identify high-value accounts and those at risk of churn.
Algorithm: K-Means Clustering applied to an RFM (Recency, Frequency, Monetary) matrix.
Inputs: The calculated recency of the last order, the frequency of orders over the past 12 months, and the total monetary value of orders placed by each customer.
Output: The assignment of each customer to a specific behavioural cluster (e.g., "VIP/High-Volume", "Consistent Regulars", "Dormant/Declining"). These outputs will populate the Customer Records module, allowing Sales Agents to target follow-ups effectively.

All three models will operate exclusively on data generated by the system itself. To ensure continuous improvement, the predictions and anomaly flags will be logged back into the MySQL database, creating a feedback loop for periodic model retraining.
"""
        replace_section("3.2.3\tModel Training", "3.2.4\tModel Validation and Testing", model_training)

        # Update TOC
        if doc.TablesOfContents.Count > 0:
            doc.TablesOfContents(1).Update()
            
        # Save as new document
        doc.SaveAs(target_doc)
        doc.Close()
        print(f"Successfully created {target_doc}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        word.Quit()

if __name__ == "__main__":
    update_document()
