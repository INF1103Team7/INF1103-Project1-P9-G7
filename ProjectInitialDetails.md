**Project Initial Details Submission**

 

Problem Statement and Target Users 

 

What real-world problem does your application aim to solve? 

 

Background information: 

Currently in schools losing your personal items is common and there isn’t a centralized platform to efficiently reunite lost belongings with their owners. Current solutions such as telegram chatgroups or physical bulletin boards help to broadcast lost items, but this can generate a lot of noise, spam and unorganized messages for the lost items owner further hindering the progress of finding their item.

 

Our goal: 

Hence with that in mind our AI driven lost and found application is designed to allow lost item owners to provide a loose freeform text description and optional image if they have on their lost item where our AI will conduct feature extraction and real time matching to reported lost items within our database to quickly provide top matches on the lost item. Increasing the efficiency of reuniting the owner with their item. 

 

Who are the intended users of the application? 

The intended users are students and staff of education institutions categorized into two main categories, the Claimants: Individuals who have misplaced their items, and the Finders: Campus staff or students who find unattended items. 

 

 

User Inputs 

 

What information or data will users provide to the system? 

The users of the application will provide the system with input data such as type of report they are going to submit, either a Lost or Found report. Subsequently a brief description of the item they have lost/found and an optional image of the item if they have. Finally, the date of occurrence. 

 

 

Use of AI 

 

How will AI be utilized within the application? 

AI will be used in two primary phases Multimodal Feature Extraction: to process the unstructured text description from the user as well as conduct feature extraction on the image that was supplied by the user (if applicable). Key features like type of item, primary and secondary color of the item, key features of the item, brand of the item, date and material of the item will be extracted. Semantic Matching: for incoming lost reports the AI will attempt to match them with existing entries within the database to generate a potential match with a similarity level and which features are matched. 

 

What outputs, insights, or recommendations will the AI generate from the user inputs? 

The AI will generate an extraction output with the key features in JSON format for found reports before storing into the database. For lost reports after extracting key features the AI will perform matching with existing data in the database in attempts to match the lost item generating a matching insights output in JSON format containing information of potential matches such as a similarity level, which features were matched and an image of the item if it was supplied. 

 

Business Rules 

 

What business rules, validations, or decision-making logic will be applied to the AI-generated outputs? 

After receiving the AI output in JSON format this layer will validate it in the correct data format and contain all the information required from the AI layer such as similarity level and key features matched before passing the output into a multi condition rule to evaluated whether it is a false positive or is the similarity score below a defined threshold before passing the top few matches back to the user to confirm whether it was their lost item.  

 

Repository Information 

URL of Repository: [https://github.com/INF1103Team7/INF1103-Ai-Powered-Scam-Message-Risk-Detector](https://github.com/INF1103Team7/INF1103-Project1-P9-G7)

 

**Data Flow Diagram**
                  ┌─────────────────────────────────────────────────────────┐
                  │                 USER SUBMITS A REPORT                   │
                  └───────────────────────────┬─────────────────────────────┘
                                              │
                                              ▼
                                 ┌─────────────────────────┐
                                 │       I/O Manager       │
                                 │ (Validate Terminal Input)
                                 └────────────┬────────────┘
                                              │
                                              ▼
                                 ┌─────────────────────────┐
                                 │       AI Manager        │
                                 │ (Multimodal Extraction) │
                                 └────────────┬────────────┘
                                              │
                                              ▼
                        ┌───────────────────────────────────────────┐
                        │      IS IT A LOST OR FOUND REPORT?        │
                        └──────────────┬────────────────────┬───────┘
                                       │                    │
                          ┌────────────┘                    └────────────┐
                          ▼                                              ▼
                 [ CASE A: LOST REPORT ]                      [ CASE B: FOUND REPORT ]
                          │                                              │
                          ▼                                              ▼
             ┌─────────────────────────┐                    ┌─────────────────────────┐
             │      Data Manager       │                    │      Data Manager       │
             │ (Save Extracted Record) │                    │ (Retrieve Active Lost)  │
             └─────────────────────────┘                    └────────────┬────────────┘
                                                                         │
                                                                         ▼
                                                            ┌─────────────────────────┐
                                                            │       AI Manager        │
                                                            │   (Semantic Matcher)    │
                                                            └────────────┬────────────┘
                                                                         │
                                                                         ▼
                                                            ┌─────────────────────────┐
                                                            │      Logic Manager      │
                                                            │ (Multi-Condition Rules) │
                                                            └────────────┬────────────┘
                                                                         │
                                                                         ▼
                                                            ┌─────────────────────────┐
                                                            │       I/O Manager       │
                                                            │  (Display Top Matches)  │
                                                            └─────────────────────────┘
