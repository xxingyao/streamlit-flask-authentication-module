# hawlucha-2-prequel

# User Stories Documentation

## 📖 Overview
This repository documents the user stories that drive our product development. Each story focuses on **who** wants something, **what** they want, and **why** it matters.

**User story format:**  
_As a `<role>`, I want `<capability>` so that `<benefit>`._

---

## Epic 1 (Creating birthday cards for the squadron)

**User Story 1**

   As a HR administrator, I want to access the unit’s personnel dates of birth so that the Commanding Officer can prepare the birthday cards to servicemen and servicewomen one month before.

  | S/N   | Sprint backlog                                                           | 
  |-------|--------------------------------------------------------------------------|
  | 1.    | Create an entity/database to store personnel's date of birth             |
  | 2.    | Create a GUI to generate list of personnel in PDF format based on filters|

## Epic 2 (Award presentations to recognise efforts and contributions to unit)

**User Story 1**

   As a HR administrator, I want to access the unit’s personnel number of years in service so that I can facilitate the distribution of 5-, 10-, and 15-year service awards when they reach the respective milestones.  

  | S/N   | Sprint backlog                                                           | 
  |-------|--------------------------------------------------------------------------|
  | 1.    | Create an entity/database to store personnel's number of years in service|
  | 2.    | Create a GUI to generate list of personnel in PDF format based on filters|

**User Story 2**

   As a HR administrator, I want to access the unit’s personnel contributions to the unit so that I can facilitate the distribution awards when requested by the Commanding Officer.  

  | S/N   | Sprint backlog                                                           | 
  |-------|--------------------------------------------------------------------------|
  | 1.    | Create an entity/database to store personnel's number of years in service|
  | 2.    | Create a GUI to generate list of personnel in PDF format based on filters|

## Epic 3 (Monitoring and allocating manpower resource)

**User Story 1**

   As a HR administrator, I want to see the number of service personnel in each flight so that I can monitor manpower levels effectively and ensure each flight has enough manpower to sustain for future plannings (etc. sending for ROA courses).  
  | S/N   | Sprint backlog                                                           | 
  |-------|--------------------------------------------------------------------------|
  | 1.    | Create an entity/database to store list of personnel in each flight                 |             
  | 2.    | Create a GUI to display list of personnel in each flight in visualisation dashboard |
  | 3.    | Create a GUI to generate list of personnel in PDF format based on filters           |
  | 4.    | Create an entity to display list of ROA/Internal/External courses available for personnels|
  | 5.    | Create an entity to display rank grade of personnel and the number of years they have been sitting on it|
  

5. **User Story 4**  
   As an HR administrator, I want to view each personnel’s personal information so that I can identify and send them for relevant courses.  

---

## Epic 4 (Control Access for Data Management)

1. **User Story 1**  
   As a System Administrator, I want to assign roles and permissions to users so that I can control who has access to what data.
   
| S/N   | Sprint backlog                                                            | 
|-------|---------------------------------------------------------------------------|
| 1.    | Create user groups and roles                                              |
| 2.    | Draft the policies for CRUD modification by roles and groups              |
| 3.    | HR administrator should have access to CRUD functions to all personal information              |
| 4.    | Operators should have access to Read functions to only their personal information to check if its accurate up to date without accessing others' information      |
| 5.    | Chief Ops should have access to Read and Update functions to Operators personal information to help ammend when any changes happens |  
| 6.    | OC should have access to Read and Update functions to t personal information        |  
| 7.    | CO should have the only access to the CEP and AFR records of all personnel so that he can analysis the man's current standing  within unit.        |  
| 8.    | CO, OC, Chief Ops and selected appointment holders should have access to all CRUD of BB personnels' IPPT & BMI record so that they can keep track of each individual's results and allow the higher ups to better help individual susceptible to failure in advance.          |

---

## Epic 5 (Ranking Exercise)

**User Story 1**

   As CO, I want to have a birds eye view of the entire squadron's performance so that I can better monitor and analysis the man's current standing within unit level and pull up those who needs help in performance  

  | S/N   | Sprint backlog                                                           | 
  |-------|--------------------------------------------------------------------------|
  | 1.    | Create an entity/database to store list of personnels' IPPT result, BMI result, AFR, and date taken                 |             
  | 2.    | Create a GUI to display list of personnels' IPPT result, BMI result, AFR and date taken in visualisation dashboard |



To do list:
- Python Script: How to let the connection not stop  when network has error, run a script which continuously scans for it.
- Documentation for SOP 
