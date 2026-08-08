<div align="center">

# INTERNSHIP PORTAL

### A Web-Based Internship Management System

**A PROJECT REPORT**

Submitted in partial fulfilment of the requirements for the degree of

**BACHELOR OF COMPUTER ENGINEERING**

Submitted by

**Ram Singh Karki**

Roll No: ______________

Under the supervision of

**______________________**

**DEPARTMENT OF COMPUTER ENGINEERING**

Affiliated to **Pokhara University**

Nepal

______________, 2082 B.S.

</div>

<div style="page-break-after: always;"></div>

## STUDENT DECLARATION

I hereby declare that the project entitled **"Internship Portal — A Web-Based Internship Management System"**, submitted to the Department of Computer Engineering in partial fulfilment of the requirements for the degree of Bachelor of Computer Engineering, is a record of the work carried out by me.

The design, the database schema, the application code and the test suite described in this report are my own work. Wherever I have used the work of others — libraries, frameworks, published articles or documentation — I have acknowledged the source in the text and listed it under References. No part of this report has been submitted earlier for the award of any other degree or diploma.

I take responsibility for the accuracy of the statements made in this report and for the correctness of the system it describes.

<br><br>

**Ram Singh Karki**

Roll No: ______________

Date: ______________

Signature: ______________________

<div style="page-break-after: always;"></div>

## SUPERVISOR ACCEPTANCE

This is to certify that the project report entitled **"Internship Portal — A Web-Based Internship Management System"** has been prepared by **Ram Singh Karki** under my supervision and guidance, in partial fulfilment of the requirements for the degree of Bachelor of Computer Engineering.

The candidate carried out the requirement analysis, database design, implementation and testing of the system personally, and reported progress to me at regular intervals during the period of the project. To the best of my knowledge, the work presented here is original and has not been submitted elsewhere for the award of any degree.

I recommend that this report be accepted for evaluation.

<br><br>

Signature: ______________________

**______________________**

Project Supervisor

Department of Computer Engineering

Date: ______________

<div style="page-break-after: always;"></div>

## APPROVAL CERTIFICATE

This is to certify that the project report entitled **"Internship Portal — A Web-Based Internship Management System"**, submitted by **Ram Singh Karki**, has been examined by the undersigned members of the evaluation committee and is hereby approved as fulfilling the project requirement for the degree of **Bachelor of Computer Engineering**.

The committee has reviewed the report, examined the working system through a live demonstration, and questioned the candidate on the design and implementation of the software.

<br><br>

| | |
|---|---|
| Signature: ______________________ | Signature: ______________________ |
| **Project Supervisor** | **Internal Examiner** |
| Date: ______________ | Date: ______________ |
| | |
| Signature: ______________________ | Signature: ______________________ |
| **External Examiner** | **Head of Department** |
| Date: ______________ | Date: ______________ |

<div style="page-break-after: always;"></div>

## ACKNOWLEDGEMENT

A project of this size is never finished alone, and I owe a good deal of it to the people around me.

My first thanks go to my project supervisor, whose questions were usually harder than the code. Asking me to justify a foreign key or explain why a page needed a role check did more for the design than any amount of extra features would have. Several decisions in Chapter 4 — particularly the cascade rules — came directly out of those discussions.

I am grateful to the Department of Computer Engineering for arranging the mid-term defence, which turned out to be the most useful checkpoint of the whole project. The feedback I received there is the reason the second half of the work went into verification, testing and documentation rather than into more screens.

I thank the faculty members who taught the courses this project draws on. The Database Management Systems course gave me normalization and the discipline of thinking in relations before thinking in pages; the Web Technology course gave me the request–response model that the whole application rests on; and Software Engineering gave me the habit of writing down requirements before writing code.

My classmates deserve mention as well. Eight of them sat with the system during beta testing, tried to break it in ways I had not imagined, and reported the confusing parts honestly. The clearer wording on the registration form and the visible status banner for unapproved accounts both came from their comments.

Finally, I thank my family for their patience through the late nights near submission.

**Ram Singh Karki**

<div style="page-break-after: always;"></div>

## ABSTRACT

Internships are a compulsory component of most technical degrees in Nepal, yet the process that surrounds them is still largely manual. Openings reach students through notice boards, messaging groups and word of mouth; applications are handed over as printed files or e-mail attachments; selection results are communicated informally; and the work a student actually does during the internship is rarely recorded anywhere the college can see. Information ends up scattered across people rather than stored in one place, and nobody holds a complete picture.

This project presents **Internship Portal**, a web application that brings the whole internship life cycle onto a single platform backed by a relational database. The system serves four kinds of users. Students register with their academic details and a supporting document, search and filter published openings, apply with a written cover letter, and — once selected — maintain a weekly log book of the work they complete. Companies publish internship openings with the skills, duration, stipend and number of vacancies, review the applicants of each opening together with their profiles and cover letters, and record a selection decision. Supervisors, who belong to a company, read the weekly logs of the students placed there and return written feedback along with marks. An administrator verifies every new account before it becomes usable, manages the user accounts, and monitors the system through a dashboard of live figures.

The application is built with Python and the Flask micro-framework, following a three-tier structure. Page logic lives in six route modules, database access goes through SQLAlchemy's object relational mapper, and the data itself is held in a MySQL database of nine normalized tables in third normal form. Referential integrity is enforced in the schema through `ON DELETE CASCADE` and `ON DELETE SET NULL` rules rather than in application code, so related records cannot be orphaned. Passwords are never stored in readable form; they are salted and hashed with Werkzeug's password utilities. Access control is applied on every route by checking both the session role and record ownership, so a company can only reach its own postings and a supervisor only the students of its own organisation. The interface is rendered server-side with Jinja2 templates that all extend one base layout and are styled with Bootstrap 5 served from the application itself, so the system runs without an internet connection.

Correctness was verified with an automated suite of thirty-three tests written using pytest, covering registration and login, internship management, the application workflow, weekly logs, role-based access control, administrative actions, cascade deletion and account verification. Every test executes against a separate database created fresh from the schema file, so the working data is never touched. All thirty-three tests pass. A round of beta testing with eight classmates produced a further set of usability corrections that were folded back into the interface.

The completed system demonstrates that a small, well-normalized relational design combined with disciplined access control is enough to replace an informal manual process end to end. Its main limitations are the absence of outbound e-mail, the use of a single combined document per student instead of individually parsed records, and deployment on a development server; each is addressed in the recommendations.

**Keywords:** internship management, Flask, SQLAlchemy, MySQL, relational database design, role-based access control, web application, normalization

<div style="page-break-after: always;"></div>

## LIST OF ABBREVIATIONS

| Abbreviation | Expansion |
|---|---|
| 3NF | Third Normal Form |
| API | Application Programming Interface |
| CRUD | Create, Read, Update, Delete |
| CSS | Cascading Style Sheets |
| CSV | Comma Separated Values |
| DBMS | Database Management System |
| DFD | Data Flow Diagram |
| ER | Entity Relationship |
| FK | Foreign Key |
| HTML | HyperText Markup Language |
| HTTP | HyperText Transfer Protocol |
| HTTPS | HyperText Transfer Protocol Secure |
| IDE | Integrated Development Environment |
| MVC | Model View Controller |
| NID | National Identity Document |
| ORM | Object Relational Mapper |
| PDF | Portable Document Format |
| PK | Primary Key |
| RAM | Random Access Memory |
| SQL | Structured Query Language |
| UI | User Interface |
| URL | Uniform Resource Locator |
| WSGI | Web Server Gateway Interface |

<div style="page-break-after: always;"></div>

## TABLE OF FIGURES

| Figure | Title | Page |
|---|---|---|
| Figure 3.1 | Gantt chart of the project schedule | |
| Figure 3.2 | Use case diagram of the Internship Portal | |
| Figure 3.3(a) | Activity diagram — registration and document upload | |
| Figure 3.3(b) | Activity diagram — administrator verification | |
| Figure 3.3(c) | Activity diagram — search, application and duplicate prevention | |
| Figure 3.3(d) | Activity diagram — selection, weekly logging and evaluation | |
| Figure 3.4 | Data flow diagram — Level 0 (context diagram) | |
| Figure 3.5 | Data flow diagram — Level 1 | |
| Figure 3.6 | Entity relationship diagram | |
| Figure 3.7 | Sequence diagram for applying to an internship | |
| Figure 4.1 | Three-tier system architecture | |
| Figure 4.2 | Class diagram of the SQLAlchemy models | |
| Figure 4.3 | Landing page | |
| Figure 4.4 | Login page | |
| Figure 4.5 | Registration role selection | |
| Figure 4.6 | Student registration form | |
| Figure 4.7 | Company registration form | |
| Figure 4.8 | Supervisor registration form | |
| Figure 4.9 | Student dashboard | |
| Figure 4.10 | Internship list | |
| Figure 4.11 | Internship search by skill | |
| Figure 4.12 | My applications | |
| Figure 4.13 | Weekly log book | |
| Figure 4.14 | Notifications | |
| Figure 4.15 | Company dashboard | |
| Figure 4.16 | Company internship list | |
| Figure 4.17 | Post internship form | |
| Figure 4.18 | Applicants of an internship | |
| Figure 4.19 | Edit internship form | |
| Figure 4.20 | Supervisor dashboard | |
| Figure 4.21 | My students | |
| Figure 4.22 | Supervisor log review | |
| Figure 4.23 | Administrator dashboard | |
| Figure 4.24 | User management | |
| Figure 4.25 | Verification queue | |

<div style="page-break-after: always;"></div>

## LIST OF TABLES

| Table | Title | Page |
|---|---|---|
| Table 2.1 | Feature comparison of related systems | |
| Table 3.1 | Functional requirements | |
| Table 3.2 | Non-functional requirements | |
| Table 3.3 | Project milestones | |
| Table 3.4 | Software requirements | |
| Table 3.5 | Hardware requirements | |
| Table 4.1 | Route table of the application | |
| Table 4.2 | Database tables and their purpose | |
| Table 4.3 | Schema of `roles` | |
| Table 4.4 | Schema of `users` | |
| Table 4.5 | Schema of `students` | |
| Table 4.6 | Schema of `companies` | |
| Table 4.7 | Schema of `supervisors` | |
| Table 4.8 | Schema of `internships` | |
| Table 4.9 | Schema of `applications` | |
| Table 4.10 | Schema of `progress_logs` | |
| Table 4.11 | Schema of `notifications` | |
| Table 4.12 | Relationships and how they are enforced | |
| Table 5.1 | Mapping of test files to test cases | |
| Table 5.2 | Test cases and results | |
| Table 6.1 | Summary of test execution | |

<div style="page-break-after: always;"></div>

## TABLE OF CONTENTS

| Section | Page |
|---|---|
| Student Declaration | i |
| Supervisor Acceptance | ii |
| Approval Certificate | iii |
| Acknowledgement | iv |
| Abstract | v |
| List of Abbreviations | vi |
| Table of Figures | vii |
| List of Tables | viii |
| **CHAPTER 1: INTRODUCTION** | **1** |
| 1.1 Background | |
| 1.2 Objectives | |
| 1.3 Purpose, Scope and Applicability | |
| 1.3.1 Purpose | |
| 1.3.2 Scope | |
| 1.3.3 Applicability | |
| 1.4 Achievements | |
| 1.5 Organization of Report | |
| **CHAPTER 2: SURVEY OF TECHNOLOGIES** | |
| 2.1 Review of Similar and Related Projects | |
| 2.2 Gaps in Existing Systems | |
| **CHAPTER 3: REQUIREMENTS AND ANALYSIS** | |
| 3.1 Problem Definition | |
| 3.2 Requirement Specification | |
| 3.3 Planning and Scheduling | |
| 3.4 Software and Hardware Requirements | |
| 3.5 Preliminary Product Description | |
| 3.6 Conceptual Models | |
| **CHAPTER 4: DESIGN** | |
| 4.1 Introduction | |
| 4.2 System Design | |
| 4.3 Database Design | |
| 4.4 Interface Design | |
| 4.5 Summary | |
| **CHAPTER 5: IMPLEMENTATION AND TESTING** | |
| 5.1 Implementation Approach | |
| 5.2 Coding Details and Code Efficiency | |
| 5.3 Testing | |
| 5.4 Modifications and Improvements | |
| 5.5 Test Cases | |
| **CHAPTER 6: RESULTS AND DISCUSSION** | |
| 6.1 Test Reports | |
| 6.2 User Documentation | |
| **CHAPTER 7: CONCLUSION AND RECOMMENDATIONS** | |
| 7.1 Conclusion | |
| 7.2 Recommendations | |
| References | |
| Annex I: Project Screenshots | |
| Annex II: Important Source Code | |
| Annex III: Testing Source Code | |

<div style="page-break-after: always;"></div>

# CHAPTER 1
# INTRODUCTION

## 1.1 Background

Every student in a technical degree in Nepal has to complete an internship before graduating. It is the point where classroom work meets an actual organisation, and for most students it is the first time their code is read by someone who is not marking it. The requirement is taken seriously by colleges; the process that supports it is not.

In practice the process runs on paper and on chat. A company that wants an intern sends a message to a lecturer it knows, or pins a notice on a board. That notice reaches whoever happens to walk past. Someone photographs it and forwards it to a group, and by the time it circulates the deadline may already have passed. A student who is genuinely interested has no way to search for openings that match what they can actually do — there is no list to search in the first place.

Applications travel the same informal path. A student prints a resume, writes a cover letter, and hands the file to a coordinator or attaches it to an e-mail. The company collects these files in whatever order they arrive. When the number of applicants grows past a handful, keeping track of who applied for which position becomes clerical work that nobody has volunteered for. Selection results are then communicated by phone or message, and rejected candidates often hear nothing at all.

The weakest part is what happens after the placement. During the internship the student is supposed to be supervised, and at the end the college is supposed to see evidence of the work. In reality the evidence is usually a report written from memory in the final week, signed by a supervisor who is remembering the same weeks equally vaguely. There is no week-by-week record while the work is still fresh, so the evaluation rests on recollection.

I chose this problem for my final year project because it is small enough to model honestly and large enough to be worth modelling. It has clear entities, clear relationships, and a workflow with real states — an opening is open or closed, an application is applied, selected or rejected, a log has feedback or does not. That maps naturally onto a relational database, which meant the project could exercise what I had learned about schema design rather than just producing screens.

The result is Internship Portal: a web application in which the internship life cycle is stored in one database and each participant sees exactly the part of it that concerns them.

## 1.2 Objectives

The objectives set at the start of the project were these.

1. **To build a centralized web application** that replaces notice boards and scattered messages with a single place where internship openings are published and found.

2. **To provide role-based access** for four kinds of users — student, company, supervisor and administrator — so that each role reaches only the pages and records it is entitled to.

3. **To design and implement a normalized relational database** in third normal form, with primary keys, foreign keys and referential integrity rules enforced by the database engine rather than by application code.

4. **To let students search and apply for internships online**, filtering the published openings by keyword and by skill, and submitting a written cover letter with each application.

5. **To record the internship itself**, through a weekly log book kept by the selected student and evaluated by a supervisor with written feedback and marks.

6. **To require institutional oversight** by making every new account pass through an administrator's verification queue before it can be used, so that no unchecked account can post an opening or apply for one.

7. **To demonstrate practical use of Flask, SQLAlchemy and MySQL** together, including object relational mapping, session management, template inheritance and server-side form handling.

8. **To verify the system with automated tests** rather than by manual clicking alone, so that a change in one part of the application does not silently break another.

## 1.3 Purpose, Scope and Applicability

### 1.3.1 Purpose

The purpose of the system is to remove the guesswork from the internship process by giving every participant a single, current view of the information that concerns them.

For a student, the purpose is visibility and record. Instead of hearing about an opening by chance, the student sees every published opening in one list and can narrow it by the skills they actually hold. Instead of wondering what happened to an application, the student sees its status change. Instead of writing a summary report from memory at the end, the student writes a short entry each week while the work is still recent.

For a company, the purpose is order. All applicants for a given opening appear together, with academic details, listed skills, cover letter and supporting document in one place, and a decision recorded against each. The company no longer maintains a private list in a spreadsheet.

For a supervisor, the purpose is a working channel. The supervisor sees the students placed at the same organisation, reads what each of them did in a given week, and responds with feedback and a mark that the student sees immediately.

For an administrator — in practice the college or the platform operator — the purpose is control. No account becomes usable until it has been checked against the document its owner uploaded, and every account on the platform can be searched, exported or removed from one page.

### 1.3.2 Scope

The system covers the internship life cycle from account creation to weekly evaluation.

Within scope:

- Registration and login for students, companies and supervisors, with hashed passwords and server-side validation.
- Mandatory document upload at student registration: the citizenship or national identity document, the resume and any other certificates are submitted as one PDF file.
- Administrator verification of every new account, with an approval or a rejection carrying a written reason.
- Publication, editing, closing and deletion of internship openings by companies, each with title, description, required skills, duration in weeks, stipend and number of vacancies.
- Keyword and skill-based search over the published openings.
- Application to an opening with a multi-line cover letter, prevention of duplicate applications, and withdrawal of a pending application by the student.
- Review of applicants by the company and recording of a selection decision.
- A weekly log book available to a student only after selection, with a week number and a description of work done.
- Supervisor feedback and marks against each weekly log, visible to the student.
- Role-specific dashboards showing live figures drawn from the database.
- A public landing page listing the participating companies with live counts.
- Administrative management of users, cascade deletion of related records, and CSV export of users and of applicants.
- In-application notifications with an unread counter, raised when an application is submitted, a decision is recorded, a weekly log is submitted, feedback is given, or an account is approved or rejected.

Outside scope:

- Outbound e-mail or SMS. Notifications are delivered inside the application only, so a user who never logs in is never told.
- Interview scheduling and direct messaging between users.
- Payment, stipend disbursement or any financial transaction.
- Automatic generation of completion certificates.
- Parsing of the uploaded document into separate structured fields.
- Deployment on a production web server with HTTPS.

### 1.3.3 Applicability

The system is written for a single institution, which is the scale at which internship placement actually happens in Nepal. A college operates it as the administrator, invites the companies it already works with, and requires its own students to register through it. Because the administrator approves every account by hand, the operator always knows exactly who is on the platform.

Three properties make it directly usable in that setting. First, it runs entirely offline: Bootstrap, its icon font and every other asset are served from the application's own static folder, so the system works on a laboratory network with no internet access. Second, it makes no assumption about the internship domain — the openings are described by free-text skills, so an information technology placement and a civil engineering placement are stored identically. Third, the administrator's verification step means the platform can be opened to registration without losing control of who is on it.

Beyond its immediate use, the design generalizes to any process where an organisation publishes opportunities, individuals apply, a decision is recorded and the resulting engagement is tracked and evaluated. Scholarship applications, research assistantships and departmental project allocation all follow the same shape.

## 1.4 Achievements

By the end of the project the following had been completed and demonstrated.

**A working system, not a prototype.** All four roles are implemented end to end. A student can be registered, approved, apply, be selected, submit logs and receive marks without any step being simulated or stubbed.

**A normalized database of nine tables** in third normal form. Role names and the three kinds of user profile are each held in their own relation, so no descriptive value is repeated across rows. Referential integrity is declared in the schema: nine foreign keys cascade on delete and one sets null, which means deleting a company removes its openings and applications automatically while a mark already awarded survives the supervisor's departure.

**Complete migration to an object relational mapper.** The application began with raw SQL statements and was rewritten so that every table is a Python class and every database operation goes through SQLAlchemy. This removed all hand-written SQL string building from the codebase, which in turn removed the injection surface that came with it.

**Enforced access control on every route.** Thirty URL rules are registered, and each protected view checks both the session role and record ownership. A company cannot open the applicants page of an opening it does not own; a supervisor cannot read the logs of a student placed at a different organisation. These are not assumptions — they are covered by automated tests.

**An administrator verification workflow.** Every account created through the portal starts in a pending state and cannot perform its main action until an administrator approves it. Rejection carries a written reason that the user is shown. This was the single largest change made after the mid-term defence.

**Thirty-three automated tests, all passing.** The suite runs against a separate database rebuilt from the schema file before each test, so it never touches working data. It covers registration, login, internship management, applications, logs, access control, administrative actions, cascade behaviour and verification.

**A search facility that works on real data.** Students filter openings by free-text keyword across the title, description and required skills, and separately by a named skill.

**A searchable user register.** The administrator can search every account by name or e-mail, page through the list ten at a time, export it as CSV, and delete an account knowing that the database will remove everything belonging to it.

**Notifications that cannot be lost.** Each of the five events that concern another party queues a message in the same transaction as the action itself, so there is no state in which an application exists but the company was never told about it.

## 1.5 Organization of Report

**Chapter 1** introduces the problem, states the objectives, and defines what the system does and does not do.

**Chapter 2** reviews existing platforms and comparable academic projects, and identifies the specific gaps this system sets out to fill.

**Chapter 3** states the problem formally and derives the requirements from it. It lists the functional and non-functional requirements, the schedule the project followed, the software and hardware needed to run it, and a set of conceptual models — use case, activity, data flow, entity relationship and sequence diagrams — that describe the system before any code is discussed.

**Chapter 4** presents the design. It explains the three-tier architecture, the folder structure, how routing and sessions work, and then gives the full database design table by table with schemas and relationships. It finishes with the interface design, describing every page of the system in terms of its purpose, inputs, outputs and navigation.

**Chapter 5** covers implementation and testing: the approach taken to writing the code, an assessment of its efficiency along five dimensions, the testing strategy at unit, integration and beta level, the modifications made in response to what testing revealed, and the full table of test cases.

**Chapter 6** reports the results of test execution and provides the user documentation — installation, setup and a walkthrough of each module from the user's point of view.

**Chapter 7** concludes, states the significance and the limitations of the work honestly, and recommends what should be done next.

The **References** follow in IEEE style, and three annexes contain the screenshots, the important source code and the testing source code.

<div style="page-break-after: always;"></div>

# CHAPTER 2
# SURVEY OF TECHNOLOGIES

## 2.1 Review of Similar and Related Projects

Before designing anything I looked at what already exists, both commercially and in the academic project literature. The systems fall into three groups, and each group taught me something different about what my own system should be.

### 2.1.1 Large professional networks — LinkedIn

LinkedIn is the reference point for anything involving job listings. Its strengths are obvious: an enormous listing base, a recommendation engine, and a profile model that carries a person's history across roles. For a student in a Nepali engineering college, however, the fit is poor in ways that matter.

The listings are national or global, so an opening in another country appears next to one in Kathmandu with no institutional filter. There is no relationship between the platform and the college, which means the college — the party that actually needs the evidence — has no visibility at all. Most importantly, LinkedIn stops at the application. Once a candidate is hired, the platform's involvement ends. Nothing on LinkedIn records what the intern did in week three, and nothing lets a supervisor grade it.

What I took from it: the value of a searchable, structured listing with explicit skill tags, and the importance of showing an applicant a clear status rather than silence.

### 2.1.2 Internship-specific platforms — Internshala

Internshala is much closer to the problem domain. It is built specifically around internships, it filters by category, location, duration and stipend, and it has a workable application flow with a cover letter. Its listing pages were a useful model for the fields an opening should carry — I arrived at title, description, required skills, duration in weeks, stipend and vacancies partly by looking at what Internshala asks employers to supply.

The gaps are again institutional. Internshala is a marketplace between a student and a company; the college is not a party to it. There is no supervisor role, no weekly reporting, and no mechanism by which a department can confirm that a registered student is genuinely its student. Verification, when it exists, is commercial rather than academic.

What I took from it: the field set for an internship record, and the observation that a cover letter needs to preserve the line breaks a student types — a small detail that Internshala gets right and that I initially got wrong.

### 2.1.3 Academic and college project systems

A number of published student projects address college-side placement management. These typically implement a student profile, a company profile, a listing table and an application table, often in PHP with MySQL. They are closest to my system in scale and intent.

Reading through several of them, two patterns recur. The first is that access control is frequently reduced to a single session variable checked at the top of a page, with no check on record ownership — meaning a user who edits a numeric identifier in the URL can often reach another user's data. The second is that the internship is treated as ending at selection; the tables stop at an applications relation, and there is nothing modelling what happens during the placement.

A related group of projects implements the supervision half — log books and evaluation — but without the discovery half, so students are enrolled by an administrator rather than applying.

What I took from these: that ownership checking must be explicit and tested rather than assumed, and that joining the discovery half to the supervision half was the contribution worth making.

### 2.1.4 The manual process

It is worth treating the existing manual process as a system in its own right, because it is what the software actually replaces. Its properties are: zero setup cost, no technology requirement, complete flexibility — and no record, no searchability, no status visibility and no way to audit anything. Any replacement has to be clearly better than a notice board on the dimensions that matter, or people will keep using the notice board.

### Table 2.1: Feature comparison of related systems

| Feature | LinkedIn | Internshala | Typical college project | Manual process | **Internship Portal** |
|---|:---:|:---:|:---:|:---:|:---:|
| Centralized listing of openings | Yes | Yes | Yes | No | **Yes** |
| Search and filter by skill | Yes | Yes | Partial | No | **Yes** |
| Online application with cover letter | Yes | Yes | Partial | No | **Yes** |
| Visible application status | Yes | Yes | Partial | No | **Yes** |
| Institutional account verification | No | No | Rarely | Implicit | **Yes** |
| Supervisor role | No | No | Rarely | Informal | **Yes** |
| Weekly progress log book | No | No | Rarely | Paper, end of term | **Yes** |
| Supervisor feedback and marks | No | No | Rarely | Informal | **Yes** |
| Record-level ownership enforcement | Yes | Yes | Often missing | N/A | **Yes** |
| Runs offline on a college network | No | No | Sometimes | Yes | **Yes** |
| Cost to the institution | Free tier | Free tier | N/A | Free | **Free** |

## 2.2 Gaps in Existing Systems

From the review above, five gaps stand out. Each one became a design decision in this project.

**Gap 1 — The supervision half is missing entirely.** Commercial platforms model a student and an employer, and they model them only up to the point of hire. Nothing in them represents the person at the host organisation who actually oversees the intern, so there is no channel through which the work can be reviewed while it is being done.

*Response in this project:* `supervisors` is a first-class table. A supervisor is a user in their own right, tied by a foreign key to the company that employs them, and that single column defines everything the supervisor may see — the selected students at that company, and no one else's.

**Gap 2 — Anyone can claim to be anyone.** On an open platform, registration is instant. That is correct for a commercial marketplace and wrong for an institutional one, where a company account represents a real organisation and a student account represents a real enrolment.

*Response in this project:* every account created through the portal enters a `pending` state. Until an administrator approves it, the account can log in and look around but cannot perform its defining action — a pending company cannot post, a pending student cannot apply, a pending supervisor cannot evaluate. Rejection carries a written reason that the user sees on every page. The student's supporting document is what the administrator reads when deciding.

**Gap 3 — The story stops at selection.** This is the largest gap. Every platform surveyed treats the placement decision as the end of its responsibility, yet from the college's point of view that is where the part it needs to assess begins.

*Response in this project:* selection creates the conditions for the second half of the workflow. A student whose application status is `selected` gains access to a weekly log book keyed to that application; a supervisor at the same company reads those entries and returns feedback and marks. The `progress_logs` table is the structural expression of this: it hangs off `applications`, not off `students`, because a log entry only means something in the context of a specific placement.

**Gap 4 — Access control is asserted rather than enforced.** In several of the academic projects reviewed, a page checks that *a* user is logged in with the right role, but not that the record being requested belongs to that user.

*Response in this project:* every protected view performs two checks. The first is the role, read from the session. The second is ownership, expressed as a filter in the query itself rather than as an `if` statement after the fact — for example, a company's applicants view queries `Internship.query.filter_by(id=internship_id, company_id=me.id)`, so a request for another company's opening returns nothing rather than returning data that is then hidden. Both checks are covered by tests.

**Gap 5 — Deleting a record leaves debris behind.** Small systems commonly delete a parent row and leave its children orphaned, so a listing survives the company that posted it and an application points at an internship that no longer exists.

*Response in this project:* every delete rule is declared in the schema and chosen by one question — does this record still mean anything once its parent is gone? Deleting a company removes its openings, their applications and the weekly logs beneath them, in one cascade the database performs itself. The one exception is the supervisor reference on a weekly log, which is set to null so that a mark already awarded survives the evaluator's departure. Test case TC-15 proves the cascade rather than assuming it.

<div style="page-break-after: always;"></div>

# CHAPTER 3
# REQUIREMENTS AND ANALYSIS

## 3.1 Problem Definition

The internship process at a typical engineering college fails in four distinct ways, and it is worth separating them because each requires a different part of the solution.

**Information does not reach the people who need it.** Openings are announced through channels that depend on chance — a notice board seen by whoever passes it, a message forwarded through a group. A student with exactly the right skills may never learn that a matching opening existed. There is no list that can be searched, so there is no way to match a student's abilities against an employer's requirement except by luck.

**Applications are unmanageable at volume.** A company that receives five applications by e-mail can cope. One that receives forty cannot, because e-mail has no notion of "applicants for this position" — the applications sit interleaved with everything else in an inbox. Deduplication is manual, the applicant's academic details arrive in whatever format the student chose, and there is nowhere to record a decision except a private spreadsheet.

**Outcomes are not communicated.** Selected candidates are usually contacted; rejected candidates frequently are not. From the student's side an application simply disappears, which makes it impossible to know whether to keep waiting or to apply elsewhere.

**The placement itself leaves no trace.** During the internship the student works for weeks with no structured reporting. At the end, a report is assembled from memory and signed by a supervisor recalling the same period equally loosely. The college, which requires the internship and grades it, receives a document produced entirely after the fact.

Formally stated, the problem is this: *the internship life cycle is a multi-party workflow with well-defined states, but it is currently executed with no shared data store, no access control and no record, so that no participant has a complete and current view of it.*

The solution therefore has to provide four things: a single persistent store for openings, applications and progress; role-appropriate views onto that store; enforced rules about who may change what; and a record of the work performed while it is being performed rather than afterwards.

## 3.2 Requirement Specification

### 3.2.1 Functional Requirements

Functional requirements were derived by walking through the workflow for each role and writing down every operation the system must support. They are numbered FR-1 to FR-24 and each is traceable to a route in Chapter 4 and to at least one test case in Chapter 5.

### Table 3.1: Functional requirements

| ID | Requirement |
|---|---|
| FR-1 | The system shall allow students, companies and supervisors to register with role-specific details. |
| FR-2 | The system shall allow a registered user to log in with an e-mail address and password, and to log out. |
| FR-3 | The system shall reject a registration that uses an e-mail address already present in the database. |
| FR-4 | The system shall store passwords only as salted hashes and shall never display or transmit them in readable form. |
| FR-5 | The system shall place every newly created account in a pending state and shall prevent it from performing its principal action until an administrator approves it. |
| FR-6 | The administrator shall be able to approve an account, or reject it with a written reason that is shown to the affected user. |
| FR-7 | A student shall upload one PDF file containing the citizenship or national identity document, the resume and any other supporting documents; the upload shall be mandatory and any other file type shall be refused. |
| FR-8 | A verified company shall be able to publish an internship with a title, description, required skills, duration in weeks, stipend and number of vacancies. |
| FR-9 | A company shall be able to edit and to delete only the internships it published. |
| FR-10 | A company shall be able to close an internship, after which it shall no longer appear to students. |
| FR-11 | The system shall display all open internships to a logged-in student. |
| FR-12 | The system shall allow a student to search internships by free-text keyword across title, description and required skills, and separately to filter by a named skill. |
| FR-13 | A verified student shall be able to apply to an open internship with a multi-line cover letter, and the line breaks entered shall be preserved when the cover letter is displayed. |
| FR-14 | The system shall prevent a student from applying more than once to the same internship. |
| FR-15 | A student shall be able to withdraw an application, and the withdrawal shall remove the application record. |
| FR-16 | A company shall be able to view all applicants for one of its internships, together with each applicant's academic details, skills, cover letter and uploaded document. |
| FR-17 | A company shall be able to record a decision on an application by setting its status to selected or rejected. |
| FR-18 | A student whose application has been selected shall be able to submit weekly log entries containing a week number and a description of the work performed. |
| FR-19 | A student whose application has not been selected shall not be able to reach the log book. |
| FR-20 | A verified supervisor shall be able to view the selected students of the company to which the supervisor belongs, and only those students. |
| FR-21 | A supervisor shall be able to record written feedback and marks against a weekly log entry, and the student shall be able to see both. |
| FR-22 | The system shall present each role with a dashboard of live figures computed from the database. |
| FR-23 | The administrator shall be able to list, search and page through all users, to export the list, and to delete a user, whereupon all records belonging to that user shall be removed. |
| FR-24 | The system shall raise an in-application notification when an application is submitted, when a decision is recorded, when a weekly log is submitted, when feedback is given and when an account is approved or rejected, and shall display the number of unread messages. |

### 3.2.2 Non-functional Requirements

### Table 3.2: Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Security | Passwords shall be stored using a salted one-way hash. Plain text passwords shall not exist anywhere in the database, the logs or the source. |
| NFR-2 | Security | All database access shall be performed through the object relational mapper using bound parameters; no query shall be assembled by string concatenation of user input. |
| NFR-3 | Security | Every protected page shall verify both the role of the session user and the ownership of the record being requested. |
| NFR-4 | Integrity | Referential integrity shall be enforced by the database engine through foreign key constraints, not by application code alone. |
| NFR-5 | Integrity | Deleting a parent record shall either remove its dependent records or null the reference, according to whether the dependent record has meaning on its own. |
| NFR-6 | Usability | A user shall be able to complete any primary task from the navigation bar within three clicks of the dashboard. |
| NFR-7 | Usability | Every action that changes data shall produce a visible confirmation or error message. |
| NFR-8 | Usability | The interface shall be usable on a laptop and on a mobile screen without horizontal scrolling. |
| NFR-9 | Performance | A page backed by the demonstration dataset shall render in under one second on the reference hardware. |
| NFR-10 | Performance | The user list, which can grow without bound, shall be paginated rather than rendered in full. |
| NFR-11 | Portability | The application shall run on Windows and on Linux with no change to the source, taking its database connection string from an environment variable. |
| NFR-12 | Availability | The application shall function with no internet connection; all front-end assets shall be served from the application itself. |
| NFR-13 | Maintainability | Each part of the site shall have its own route module, and each database table its own model class. |
| NFR-14 | Testability | The behaviour of the system shall be verifiable by an automated test suite running against a separate database. |
| NFR-15 | Reliability | The test suite shall pass in full before any change is considered complete. |

## 3.3 Planning and Scheduling

The project ran across sixteen weeks in two phases separated by the mid-term defence. The first phase produced a working system with core CRUD; the second phase, informed by the defence, added verification, testing and documentation.

### Table 3.3: Project milestones

| # | Milestone | Completed by | Deliverable |
|---|---|---|---|
| M1 | Problem finalized, requirements agreed with supervisor | Week 2 | Requirement list |
| M2 | Database schema designed and normalized | Week 4 | ER diagram, `database.sql` |
| M3 | Authentication and role-based routing working | Week 6 | Login, registration, dashboards |
| M4 | Core CRUD complete — internships, applications | Week 8 | **Mid-term defence** |
| M5 | Weekly logs and supervisor evaluation | Week 10 | Log book, feedback and marks |
| M6 | Migration from raw SQL to SQLAlchemy ORM | Week 11 | `models.py` |
| M7 | Account verification workflow | Week 13 | Admin approval queue with reasons |
| M8 | Automated test suite, all cases passing | Week 14 | `tests/`, 36 tests |
| M9 | Interface refinement, demonstration data, screenshots | Week 15 | Bootstrap UI, `seed_demo.py` |
| M10 | Report, presentation, final defence | Week 16 | **Final defence** |

Figure 3.1 shows the same schedule as a Gantt chart. A solid bar marks the weeks in which an activity was active, and a diamond marks each defence.

![](diagrams/fig3_1_gantt.png)

**Figure 3.1: Gantt chart of the project schedule**

## 3.4 Software and Hardware Requirements

### Table 3.4: Software requirements

| Software | Version | Purpose |
|---|---|---|
| Python | 3.10 or later | Language the application is written in |
| Flask | 3.x | Web framework: routing, request handling, sessions, templating |
| Flask-SQLAlchemy | 3.x | Integration of the SQLAlchemy ORM with the Flask application context |
| SQLAlchemy | 2.x | Object relational mapper; generates SQL and maps rows to objects |
| PyMySQL | 1.x | Pure-Python driver through which SQLAlchemy speaks to MySQL |
| Werkzeug | bundled with Flask | Password hashing and secure filename handling |
| Jinja2 | bundled with Flask | Server-side template engine |
| MySQL or MariaDB | 8.0 / 10.5 or later | Relational database management system |
| Bootstrap | 5.3 | Front-end component and grid framework, served locally |
| Bootstrap Icons | 1.11 | Icon font used on buttons and navigation, served locally |
| pytest | 8.x | Test runner for the automated suite |
| Visual Studio Code | current | Development environment |
| Git and GitHub | current | Version control and remote backup |
| A modern web browser | current | Client — Chrome, Edge or Firefox |

The four packages that must be installed with `pip` are listed in `requirements.txt`: Flask, Flask-SQLAlchemy, PyMySQL and pytest. Everything else arrives as a dependency of those or is vendored into the `static/` folder.

### Table 3.5: Hardware requirements

| Component | Minimum | Recommended |
|---|---|---|
| Processor | Dual core, 2.0 GHz | Quad core, 2.5 GHz or better |
| Memory | 4 GB RAM | 8 GB RAM |
| Storage | 2 GB free | 5 GB free |
| Display | 1366 × 768 | 1920 × 1080 |
| Network | Not required — the system runs on `localhost` | Local area network if accessed from other machines |

The system was developed and tested on a laptop with an Intel Core i5 processor and 8 GB of memory, running the application and the database server on the same machine.

## 3.5 Preliminary Product Description

Internship Portal is a server-rendered web application. A user opens it in a browser, and every page is produced on the server by a Flask view function that queries the database through SQLAlchemy and renders a Jinja2 template. There is no client-side application state and no separate front-end build; the browser receives finished HTML.

The product presents itself differently to each of its four roles, from one codebase and one database.

**As a visitor**, before logging in, the user sees a public landing page carrying live counts of registered students, companies, supervisors and internships, followed by a card for each participating company showing its industry, location and number of open positions. This page exists to make the platform look inhabited rather than empty, and every number on it is a live query.

**As a student**, the user registers with academic details and a mandatory PDF of supporting documents. After the administrator approves the account, the student browses open internships, narrows them by keyword or skill, applies with a cover letter, tracks each application's status, and — once selected — keeps a weekly log book that the supervisor annotates with feedback and marks.

**As a company**, the user registers with industry, location and description, and after approval publishes internships, edits or closes them, reviews the applicants of each with their full profiles and cover letters, records selection decisions, and exports an applicant list as CSV.

**As a supervisor**, the user registers under an existing company, and after approval sees the selected students at that company, reads their weekly entries, and records feedback and a mark out of ten against each entry.

**As an administrator**, the user works through a verification queue of pending accounts — reading the student's uploaded document before deciding — approves or rejects with a written reason, searches and pages through all users, exports the user list, and deletes accounts when necessary.

Cutting across all four roles are two mechanisms. The verification state shows as a banner until an administrator approves the account, and the routes that change data refuse to run before then. A notification bell in the navigation bar carries the number of unread messages and links to the list of events that concern the user.

## 3.6 Conceptual Models

This section models the system before any implementation detail. The diagrams progress from the outside in: first who uses the system and for what, then the flow of activity through it, then the flow of data, then the structure of the stored data, and finally the ordered interaction that produces one specific outcome.

### 3.6.1 Use Case Diagram

The use case diagram identifies four actors and the operations each may perform. Student, Company and Supervisor are external actors who register themselves; Administrator is an internal actor whose account is created with the database. Register and Login are shared by the three self-registering actors, which is why they sit at the boundary between them.

The diagram makes one structural point that matters later: *Apply for Internship* and *Maintain Weekly Log* both belong to Student, but the second is only reachable after Company has performed *Select or Reject Applicant*. The dependency between actors is real, not decorative.

![](diagrams/fig3_2_use_case.png)

**Figure 3.2: Use case diagram of the Internship Portal**

Four dependencies between these use cases are not visible as symbols but matter more than any of them individually. *Verify / Reject Accounts* gates both *Apply with Cover Letter* and *Post / Edit / Close Internship*: neither is possible while an account is still pending. *Select or Reject Applicant* is what enables *Maintain Weekly Log Book*, and a log entry in turn has to exist before *Review Logs & Give Feedback* can act on it. Each of those four rules is enforced in code and covered by a test case.

### 3.6.2 Activity Diagram

The activity diagram traces the internship life cycle from the moment a student decides to register to the moment a supervisor records marks. Because the flow spans three roles and a dozen decision points, it is presented in four connected stages; the terminal node of each stage names the figure that continues it.

```mermaid
%%{init: {"flowchart": {"rankSpacing": 28, "nodeSpacing": 28, "padding": 6}} }%%
flowchart TD
    START((Start)) --> A1[Student opens portal<br/>and registers]
    A1 --> A2[/Upload one PDF:<br/>NID + resume + documents/]
    A2 --> D1{Valid PDF<br/>supplied?}
    D1 -->|No| A3[Show error:<br/>one PDF required]
    A3 --> A2
    D1 -->|Yes| A4[(Create user + student row<br/>status = pending)]
    A4 --> GO((Go to<br/>Figure 3.3b))
    style A4 fill:#dbeafe,stroke:#2563eb
    style GO fill:#e0e7ff,stroke:#4338ca
```

**Figure 3.3(a): Registration and document upload**

A registration cannot complete without an acceptable PDF; the loop back to the upload step is the visual form of that rule.

```mermaid
%%{init: {"flowchart": {"rankSpacing": 28, "nodeSpacing": 28, "padding": 6}} }%%
flowchart TD
    IN((Pending<br/>account)) --> A5[Administrator opens<br/>verification queue]
    A5 --> A6[Read the uploaded PDF:<br/>NID, resume, certificates]
    A6 --> D2{Approve?}
    D2 -->|Reject| A7[(status = rejected<br/>reason recorded)]
    A7 --> END1((Account<br/>unusable))
    D2 -->|Approve| A8[(status = verified)]
    A8 --> GO((Go to<br/>Figure 3.3c))
    style A7 fill:#dbeafe,stroke:#2563eb
    style A8 fill:#dbeafe,stroke:#2563eb
    style END1 fill:#fee2e2,stroke:#dc2626
    style GO fill:#e0e7ff,stroke:#4338ca
```

**Figure 3.3(b): Administrator verification**

The administrator reads the uploaded document before deciding. A rejection is a terminal state for the account until the administrator revisits it, and the reason given is shown to the user.

```mermaid
%%{init: {"flowchart": {"rankSpacing": 28, "nodeSpacing": 28, "padding": 6}} }%%
flowchart TD
    IN((Verified<br/>student)) --> A9[Search internships;<br/>filter by keyword or skill]
    A9 --> D3{Suitable<br/>opening found?}
    D3 -->|No| A9
    D3 -->|Yes| A11[Write cover letter<br/>and submit]
    A11 --> D4{Already applied?}
    D4 -->|Yes| A12[Refuse:<br/>duplicate application]
    A12 --> A9
    D4 -->|No| A13[(Create application<br/>status = applied)]
    A13 --> GO((Go to<br/>Figure 3.3d))
    style A13 fill:#dbeafe,stroke:#2563eb
    style GO fill:#e0e7ff,stroke:#4338ca
```

**Figure 3.3(c): Search, application and duplicate prevention**

Two loops return the student to the search step: one when nothing suitable is found, and one when an application to that opening already exists.

```mermaid
%%{init: {"flowchart": {"rankSpacing": 28, "nodeSpacing": 28, "padding": 6}} }%%
flowchart TD
    IN((Application<br/>received)) --> A15[Company reads profile, skills,<br/>cover letter and document]
    A15 --> D5{Decision}
    D5 -->|Rejected| A17[(status = rejected)]
    A17 --> END2((Application<br/>closed))
    D5 -->|Selected| A19[(status = selected<br/>log book unlocked)]
    A19 --> A22[Student writes week entry:<br/>week number + work done]
    A22 --> A25[Supervisor writes feedback<br/>and awards marks]
    A25 --> D6{Internship<br/>period over?}
    D6 -->|No| A22
    D6 -->|Yes| END3((Internship<br/>complete))
    style A17 fill:#dbeafe,stroke:#2563eb
    style A19 fill:#dbeafe,stroke:#2563eb
    style END2 fill:#fef3c7,stroke:#d97706
    style END3 fill:#dcfce7,stroke:#16a34a
```

**Figure 3.3(d): Selection, weekly logging and evaluation**

The loop at the foot of Figure 3.3(d) is the one worth dwelling on: the log-and-feedback cycle repeats every week for the duration of the placement, which is exactly why `progress_logs` carries a week number and one row per week rather than a single summary field per placement.

### 3.6.3 Data Flow Diagram — Level 0 (Context Diagram)

The context diagram treats the whole system as a single process and shows only what crosses its boundary. Four external entities exchange data with it.

![](diagrams/fig3_4_dfd0.png)

**Figure 3.4: Data flow diagram — Level 0 (context diagram)**

Nothing enters or leaves the system except through these four entities. There is no external service, no payment gateway and no mail server, which is a deliberate property: the system is self-contained and can run on an isolated network.

### 3.6.4 Data Flow Diagram — Level 1

Level 1 opens the single process of Figure 3.4 into eight numbered processes and shows the data stores each one reads and writes. Process 8.0 exists because a data store may never be connected straight to an external entity: a user reads the notification list through a process, not by reaching into the table.

![](diagrams/fig3_5_dfd1.png)

**Figure 3.5: Data flow diagram — Level 1**

One observation follows directly from this diagram: process 2.0 stands between registration and every productive process. Both 3.0 and 4.0 read the verified status from D1 before acting, which is the data-flow expression of the verification gate. Nothing a user creates reaches D3 or D4 until an administrator has approved the account behind it.

### 3.6.5 Entity Relationship Diagram

The entity relationship diagram shows the nine relations of the database, their attributes, and the cardinality of every association between them.

```mermaid
erDiagram
    ROLES ||--o{ USERS : "defines"
    USERS ||--o| STUDENTS : "extends"
    USERS ||--o| COMPANIES : "extends"
    USERS ||--o| SUPERVISORS : "extends"
    COMPANIES ||--o{ INTERNSHIPS : "posts"
    COMPANIES ||--o{ SUPERVISORS : "employs"
    STUDENTS ||--o{ APPLICATIONS : "submits"
    INTERNSHIPS ||--o{ APPLICATIONS : "receives"
    APPLICATIONS ||--o{ PROGRESS_LOGS : "contains"
    SUPERVISORS ||--o{ PROGRESS_LOGS : "evaluates"

    ROLES {
        int id PK
        varchar role_name UK "admin/student/company/supervisor"
    }
    USERS {
        int id PK
        int role_id FK
        varchar name
        varchar email UK
        varchar password "salted hash"
        varchar verification_status "pending/verified/rejected"
        varchar verification_remarks
        datetime verified_at
        datetime created_at
    }
    STUDENTS {
        int id PK
        int user_id FK "unique"
        varchar roll_number
        varchar department
        int semester
        varchar skills
        varchar document_url "one PDF"
    }
    COMPANIES {
        int id PK
        int user_id FK "unique"
        varchar industry
        varchar location
        text description
    }
    SUPERVISORS {
        int id PK
        int user_id FK "unique"
        int company_id FK
        varchar designation
        varchar department
    }
    INTERNSHIPS {
        int id PK
        int company_id FK
        varchar title
        text description
        varchar required_skills
        int duration_weeks
        varchar stipend
        int vacancies
        varchar status "open/closed"
        datetime posted_date
    }
    APPLICATIONS {
        int id PK
        int student_id FK
        int internship_id FK
        text cover_letter
        varchar status "applied/selected/rejected"
        datetime applied_date
    }
    PROGRESS_LOGS {
        int id PK
        int application_id FK
        int supervisor_id FK
        int week_number
        text description
        text feedback
        int marks
        datetime submitted_date
    }
```

**Figure 3.6: Entity relationship diagram**

The design rests on one decision that shapes everything else: `users` is a single login relation, and the three role-specific relations extend it one-to-one rather than duplicating its columns. A name, e-mail address and password hash exist in exactly one place regardless of the account's role. Chapter 4 develops this and the cascade rules in full.

### 3.6.6 Sequence Diagram

The sequence diagram takes one operation — a student applying to an internship — and shows the ordered exchange between the browser, the routing layer, the view function, the ORM and the database. This is the interaction that exercises the largest number of the system's rules at once: authentication, role checking, verification, duplicate prevention and notification.

```mermaid
sequenceDiagram
    autonumber
    actor S as Student (Browser)
    participant F as Flask (app.py)
    participant R as student.apply()
    participant M as SQLAlchemy Models
    participant DB as MySQL Database

    S->>F: POST /apply/12 (cover_letter)
    F->>F: Match URL rule to view function
    F->>R: Invoke apply(internship_id=12)

    R->>R: Read session['role']
    alt role is not 'student'
        R-->>S: 302 Redirect to /login
    end

    R->>M: verified_only('apply for internships')
    M->>DB: SELECT * FROM users WHERE id = ?
    DB-->>M: user row
    M-->>R: None (verified) or message
    alt account still pending or rejected
        R-->>S: Flash message + redirect to /internships
    end

    R->>M: current_student()
    M->>DB: SELECT * FROM students WHERE user_id = ?
    DB-->>M: student row
    M-->>R: Student object

    R->>M: Application.query.filter_by(student_id, internship_id)
    M->>DB: SELECT * FROM applications WHERE student_id = ? AND internship_id = ?
    DB-->>M: empty result
    M-->>R: None

    alt duplicate application exists
        R-->>S: "You already applied to this internship."
    else no previous application
        R->>M: db.session.add(Application(...))
                R->>M: db.session.commit()
        M->>DB: INSERT INTO applications (...)
        DB-->>M: COMMIT successful
        M-->>R: Persisted
        R-->>S: 302 Redirect to /my_applications<br/>+ "Application submitted!"
    end

    Note over DB: The duplicate check and the insert<br/>happen in one transaction, so two<br/>applications can never both be written.
```

**Figure 3.7: Sequence diagram for applying to an internship**

The final note is the important one. The application row and the notification to the company are queued on the session and written by a single `commit()`, so either both exist or neither does. There is no state in which an application was recorded but the company was never told about it. Behind the duplicate check, the `UNIQUE (student_id, internship_id)` constraint in the schema is the second line of defence.

<div style="page-break-after: always;"></div>

# CHAPTER 4
# DESIGN

## 4.1 Introduction

Chapter 3 described what the system must do. This chapter describes how it is put together to do it.

The design follows one principle throughout: each piece of the system should have exactly one job, and it should be obvious from the file layout which piece does what. That principle is not decoration. It is what made the project maintainable through a mid-term rewrite, a migration from raw SQL to an object relational mapper, and the later addition of a verification workflow that touched almost every route.

Three decisions shape everything that follows.

The first is that the application is **server-rendered**. Every page is produced in full on the server and delivered as finished HTML. There is no client-side framework, no JSON API and no browser-side state. This keeps the trust boundary simple — the browser never holds anything the server has not already decided it may see — and it means the security argument for the whole system reduces to the security argument for each route.

The second is that **the database, not the application, owns integrity**. Foreign keys, uniqueness constraints and delete rules are declared in the schema. Application code does not check whether a company still exists before deleting its internships; the constraint does that, correctly, every time, including in paths the programmer forgot about.

The third is that **routing is a flat, readable table**. Flask offers blueprints for structuring larger applications, and I chose not to use them. Instead `app.py` registers every URL of the site with `app.add_url_rule()` in one place. The result is a file that can be read top to bottom as a table of contents for the entire application, which was worth more to this project than the modularity blueprints would have added.

## 4.2 System Design

### 4.2.1 Overall Architecture

The system uses the classic three-tier arrangement: a presentation tier in the browser, an application tier in Flask, and a data tier in MySQL. The tiers communicate only with their immediate neighbours.

**Figure 4.1: Three-tier system architecture** *(see `docs/system_architecture.png`)*

The **presentation tier** is the user's browser. It renders HTML, submits forms and follows links. It holds no business logic whatsoever. A student's browser has no knowledge of what a student may or may not do; it merely displays whatever the server sent and posts whatever the user typed.

The **application tier** is the Flask process. It receives an HTTP request, matches the URL against the routing table in `app.py`, and calls the corresponding view function in one of the six route modules. That function reads the session to establish who is asking, checks that this person is permitted to perform the operation, works with the data through the model classes, and renders a Jinja2 template into HTML. All decisions happen here.

The **data tier** is MySQL, holding nine related tables. It receives parameterized SQL generated by SQLAlchemy and returns result rows, which SQLAlchemy converts into Python objects before the view function ever sees them.

The traffic between tiers is worth stating precisely, because it is what makes the design defensible. Between browser and Flask: an HTTP request carrying form data, and an HTTP response carrying rendered HTML. Between Flask and MySQL: SQL with values supplied as bound parameters, and result rows returned as objects. At no point does a value typed by a user travel to the database as part of a query string.

### 4.2.2 Folder Structure

```
Internship_Portal/
│
├── app.py                  Application object, configuration, and the
│                           complete URL routing table (32 rules)
├── models.py               Nine SQLAlchemy model classes plus the
│                           shared helper functions
├── database.sql            Schema: CREATE TABLE statements, constraints,
│                           and the seed rows for roles and the admin
├── seed_demo.py            Generates the demonstration dataset
├── requirements.txt        Flask, Flask-SQLAlchemy, PyMySQL, pytest
├── run_tests.bat           Convenience script for running the suite
│
├── routes/                 One module per area of the site
│   ├── __init__.py
│   ├── auth.py             Register (three forms), login, logout
│   ├── main.py             Landing page, dashboard, internship list,
│   │                       search
│   ├── student.py          Apply, my applications, withdraw, weekly logs
│   ├── company.py          Post / edit / delete internships, applicants,
│   │                       selection decisions, CSV export
│   ├── supervisor.py       My students, view logs, give feedback
│   └── admin.py            Users, verification queue, CSV export
│
├── templates/              Nineteen Jinja2 templates
│   ├── base.html           The one layout every other page extends
│   ├── index.html          Public landing page
│   ├── login.html
│   ├── register.html       Role selection
│   ├── register_student.html
│   ├── register_company.html
│   ├── register_supervisor.html
│   ├── dashboard.html      Role-specific figures
│   ├── internships.html    List with search
│   ├── add_internship.html
│   ├── edit_internship.html
│   ├── applicants.html
│   ├── my_applications.html
│   ├── my_logs.html        Student's log book
│   ├── students.html       Supervisor's student list
│   ├── view_logs.html      Supervisor's log review
│   ├── users.html          Admin user management
│   └── verifications.html  Admin verification queue
│
├── static/
│   ├── bootstrap.min.css       Vendored — no internet needed
│   ├── bootstrap.bundle.min.js
│   ├── bootstrap-icons.css
│   ├── fonts/                  Icon font files
│   ├── style.css               The project's own overrides
│   ├── logo.png                Full logo (landing page)
│   ├── logo_mark.png           Icon mark (navigation bar, favicon)
│   └── uploads/                Student documents, created at start-up
│
├── tests/                  Thirty-three automated tests
│   ├── conftest.py         Fixtures and shared helpers
│   ├── test_01_authentication.py  … test_11_verification.py
│   └── README.md           Mapping of test files to test cases
│
└── docs/                   Report, diagrams and screenshots
```

The rule is one file, one responsibility. When a bug appeared in the supervisor's feedback handling, there was exactly one file to open.

### 4.2.3 Backend Design

The backend is Python. Each view function follows the same four-step shape, and the consistency is deliberate — a reader who understands one route understands all of them:

1. **Establish identity and permission.** Read `session['role']`; redirect to the login page if it is not the expected role. Where the operation changes data, additionally call `verified_only()` to confirm the administrator has approved the account.
2. **Fetch the acting user's own record.** `current_student()`, `current_company()` or `current_supervisor()` returns the profile row belonging to the session user.
3. **Perform the operation.** Query, insert, update or delete through the model classes, scoping every query by ownership.
4. **Respond.** Either render a template or redirect with a flash message.

Five shared helpers in `models.py` remove duplication across the routes. `verified_only(action)` returns `None` when the account is verified and an explanatory message when it is pending or rejected — the message differs, and a rejected user is shown the administrator's stated reason. `notify(user_id, message, link)` queues an in-application message, written on the caller's next commit so it shares the transaction of the action that caused it. The three `current_*()` functions each return the profile row belonging to the session user, collapsing a query pattern that would otherwise be repeated in every route.

Three context processors registered in `app.py` inject values into every template without any route having to pass them: whether a logo file is present, the verification status of the current user together with the count of pending accounts for administrators, and the number of unread notifications for the bell badge.

### 4.2.4 Frontend Design

The front end is HTML5, CSS3 and Bootstrap 5, assembled by Jinja2 on the server.

Template inheritance carries most of the weight. `base.html` holds the document skeleton, the stylesheet links, the navigation bar, the flash-message area, the account-status banner and the footer, and declares a single `{% block content %}`. Every other template begins with `{% extends 'base.html' %}` and fills that block. The navigation bar is built once and adapts to the session — a student sees "My Applications", a company sees "Post Internship", a supervisor sees "My Students", an administrator sees the verification queue with a red badge showing how many accounts are waiting.

Bootstrap is vendored into `static/` rather than loaded from a content delivery network. This was a deliberate choice made after a laboratory session where the network was unavailable and a page rendered without any styling at all. The system now has no external dependency at run time.

`style.css` is short on purpose. It contains the project's own additions only: the brand colours, the card treatment on the landing page, the `preserve` class that keeps a cover letter's line breaks intact using `white-space: pre-wrap`, and the sizing of the logo in the navigation bar.

Bootstrap Icons appear on every button and navigation link. An icon alone is ambiguous, so each is paired with its label — `<i class="bi bi-person-plus me-1"></i>Register` — which keeps the interface readable for a first-time user.

### 4.2.5 Routing

All thirty URL rules are registered in `app.py`. Table 4.1 is that routing table.

### Table 4.1: Route table of the application

| URL | Methods | View function | Purpose |
|---|---|---|---|
| `/` | GET | `main.home` | Public landing page with live counts and partner cards |
| `/dashboard` | GET | `main.dashboard` | Role-specific figures |
| `/internships` | GET | `main.internships` | Internship list with keyword and skill search |
| `/notifications` | GET | `main.notifications` | Notification list; marks all as read |
| `/register` | GET | `auth.register` | Role selection page |
| `/register/student` | GET, POST | `auth.register_student` | Student registration with document upload |
| `/register/company` | GET, POST | `auth.register_company` | Company registration |
| `/register/supervisor` | GET, POST | `auth.register_supervisor` | Supervisor registration under a company |
| `/login` | GET, POST | `auth.login` | Authentication |
| `/logout` | GET | `auth.logout` | Clears the session |
| `/apply/<int:internship_id>` | POST | `student.apply` | Submit an application with a cover letter |
| `/my_applications` | GET | `student.my_applications` | The student's own applications |
| `/withdraw/<int:id>` | POST | `student.withdraw` | Withdraw an application |
| `/my_logs/<int:application_id>` | GET, POST | `student.my_logs` | Weekly log book for a selected application |
| `/internships/add` | GET, POST | `company.add_internship` | Publish an internship |
| `/internships/edit/<int:id>` | GET, POST | `company.edit_internship` | Edit or close an internship |
| `/internships/delete/<int:id>` | POST | `company.delete_internship` | Delete an internship |
| `/applicants/<int:internship_id>` | GET | `company.applicants` | Applicants of one internship |
| `/applicants/<int:internship_id>/export` | GET | `company.applicants_export` | Applicant list as CSV |
| `/applications/<int:id>/status` | POST | `company.update_status` | Record a selection decision |
| `/students` | GET | `supervisor.students` | Selected students at the supervisor's company |
| `/logs/<int:application_id>` | GET | `supervisor.view_logs` | One student's weekly logs |
| `/logs/<int:log_id>/feedback` | POST | `supervisor.give_feedback` | Record feedback and marks |
| `/users` | GET | `admin.users` | User list with search and pagination |
| `/users/export` | GET | `admin.users_export` | User list as CSV |
| `/users/delete/<int:id>` | POST | `admin.delete_user` | Delete a user and cascade |
| `/verifications` | GET | `admin.verifications` | Verification queue filtered by status |
| `/verify/<int:id>` | POST | `admin.verify_user` | Approve an account |
| `/reject/<int:id>` | POST | `admin.reject_user` | Reject an account with a reason |

Two conventions are visible in the table. Anything that changes data is `POST` only; a destructive operation cannot be triggered by following a link. And record identifiers in URLs are typed as `<int:...>`, so a request such as `/applicants/abc` never reaches the view function at all — Flask rejects it during routing.

### 4.2.6 Database Flow

A concrete request makes the flow easiest to follow. A student submits the apply form on internship 12.

1. The browser sends `POST /apply/12` carrying the cover letter.
2. Flask matches the rule `/apply/<int:internship_id>` and calls `student.apply(internship_id=12)`.
3. The function reads `session['role']`. If it is not `student`, it redirects and stops.
4. `verified_only('apply for internships')` loads the user and returns a message if the account is pending or rejected. If so, the message is flashed and the function stops.
5. `current_student()` issues `SELECT * FROM students WHERE user_id = ?` and returns a `Student` object.
6. A duplicate check queries `applications` for the same student and internship. If a row exists, the student is told and nothing is written.
7. Otherwise an `Application` object is constructed and added to the session, and `notify()` queues a message for the company that owns the internship.
8. `db.session.commit()` writes all three rows in one transaction.
9. The function redirects to `/my_applications` with a success message.

Steps 7 and 8 are the point of interest. Three inserts into three different tables succeed or fail together. The system cannot end up in a state where an application exists but the company was never notified.

### 4.2.7 Authentication

Authentication is session-based and deliberately plain.

When an account is created, `User.set_password()` calls Werkzeug's `generate_password_hash()`, which produces a salted PBKDF2 hash. That string is what the `password` column stores. The original text is never written anywhere.

At login, the user's e-mail is used to fetch the row, and `check_password()` calls `check_password_hash()` to compare the supplied password against the stored hash. Because the hash is one-way, a database dump does not reveal anybody's password. On success three values go into the Flask session: `user_id`, `name` and `role`. The session cookie is signed with the application's secret key, so a user cannot edit it to promote themselves to administrator — any modification invalidates the signature and the session is discarded.

A failed attempt produces the same message whether the address exists or not, so the login page cannot be used to discover which e-mail addresses are registered.

Logout calls `session.clear()`.

### 4.2.8 Authorization

Authorization is applied at three levels, and the layering is what makes it hold.

**Level 1 — Role.** Every protected view begins by comparing `session.get('role')` against the role that owns the page. A student who requests `/users` is redirected to the login page.

**Level 2 — Verification.** Views that change data call `verified_only()`. This is separate from the role check because a pending company is legitimately a company; it simply may not act yet. The distinction matters for the message the user receives.

**Level 3 — Ownership.** This is the level most often missed, so it is worth stating exactly how it is implemented. Ownership is expressed *inside the query*, not as a test after the fact:

```python
internship = Internship.query.filter_by(id=internship_id, company_id=me.id).first()
if not internship:
    flash('Internship not found.')
    return redirect(url_for('internships'))
```

A company requesting another company's internship receives `None` from the database, not a row that is then hidden. The same pattern scopes a student's withdrawal to their own applications, a supervisor's log access to their own company, and a student's log book to an application that is both theirs and `selected`. Test case TC-14 covers both the role level and the ownership level.

One further rule sits outside this scheme: an administrator cannot delete their own account. Without it, a single click could leave the system with no administrator at all.

### 4.2.9 Validation

Validation happens on both sides, with the server treated as the only authority.

In the browser, HTML5 attributes give immediate feedback: `required` on mandatory fields, `type="email"` on addresses, `type="number"` with `min` and `max` on the semester, and `accept=".pdf"` on the document upload. These are conveniences. They can be bypassed by anyone who opens the developer tools, and the design assumes they will be.

On the server, the checks that actually matter are enforced regardless of what the browser did:

- **Duplicate e-mail** — `_email_taken()` queries the `users` table before any row is created.
- **Document type** — the uploaded filename's extension is checked against `ALLOWED_EXTENSIONS`, which contains `pdf` alone. Anything else is refused, and registration does not proceed.
- **Document presence** — a student registration with no usable file is rejected outright.
- **Duplicate application** — the `applications` table is queried for the same student and internship before an insert.
- **Duplicate college** — the name is checked before insertion.
- **Numeric fields** — empty strings are converted to `None` rather than being passed through, so the database stores a null instead of failing on an empty value.
- **File names** — `secure_filename()` strips path separators, and a timestamp prefix prevents one upload from overwriting another.

Constraints in the schema act as the final layer: `UNIQUE` on `users.email` and `roles.role_name`, `UNIQUE (student_id, internship_id)` on `applications`, and `NOT NULL` on every column the application depends on.

### 4.2.10 Session Management

The session is a signed cookie holding three values and nothing else: `user_id`, `name` and `role`. Keeping it small is intentional. Anything more would be a second copy of information the database already holds, and copies drift — if an administrator changed a user's role, a session carrying a stale copy of the profile would be wrong until the user logged out.

Because only the identifier is stored, every request re-reads what it needs. The context processor that supplies the verification banner loads the user afresh on each render, so an account approved a moment ago shows as approved on the very next page.

The signature is produced with `app.secret_key`, which is read from the `SECRET_KEY` environment variable and falls back to a development value. Section 7.2 recommends that a deployment always set the variable.

### 4.2.11 Security Measures

The measures in place, and the reasoning behind each:

**Passwords are salted hashes.** Werkzeug's PBKDF2 implementation. Two users with the same password have different stored values, so a leaked table does not reveal shared passwords.

**No SQL is built by string concatenation.** Every query goes through SQLAlchemy, which sends values as bound parameters. A student typing `'; DROP TABLE users; --` into the search box searches for that literal string. This was not true of the first version of the project, which built SQL with f-strings; removing them was one of the more valuable changes made during the ORM migration.

**Sessions are signed.** A tampered cookie is rejected.

**Authorization is checked on every route, at three levels.** Section 4.2.8.

**Uploads are constrained.** Type restricted to PDF, filename sanitized, name prefixed with a timestamp.

**Destructive operations require POST.** No deletion can be caused by a link.

**Failed logins are recorded.** With the attempted address and a null user.

**Identifiers in URLs are typed.** Non-numeric values are rejected during routing.

Two measures are deliberately absent and are declared as such rather than glossed over. There is **no CSRF protection** — the forms carry no anti-forgery token, and a production deployment should add Flask-WTF's `CSRFProtect`. And the application runs on the **Flask development server**, which is single-threaded and not intended for public exposure. Both are listed in Section 7.1.2 and Section 7.2.

## 4.3 Database Design

### 4.3.1 Overview

The database is named `internship_db` and contains nine tables. It is created by `database.sql`, which holds the `CREATE TABLE` statements, the foreign key constraints with their delete rules, and the seed rows for the four roles and the initial administrator account.

### Table 4.2: Database tables and their purpose

| # | Table | Purpose | Rows in demonstration data |
|---|---|---|---|
| 1 | `roles` | The four role names | 4 |
| 2 | `users` | Central login record for every account | 30 |
| 3 | `students` | Academic profile extending a user | 18 |
| 4 | `companies` | Organisation profile extending a user | 5 |
| 5 | `supervisors` | Supervisor profile extending a user, tied to a company | 6 |
| 6 | `internships` | Openings published by companies | 12 |
| 7 | `applications` | A student's application to an opening | 33 |
| 8 | `progress_logs` | Weekly entries with supervisor feedback and marks | 16 |
| 9 | `notifications` | In-application messages with an unread flag | 20 |

### 4.3.2 Table Design

Each table is given below with its columns, types, constraints and a note on why it exists in this form.

#### Table 4.3: Schema of `roles`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `role_name` | VARCHAR(20) | NOT NULL, UNIQUE | `admin`, `student`, `company`, `supervisor` |

A separate relation rather than a text column on `users`. Storing the word "student" against every student row would repeat the same value thousands of times and would allow a typo to create a fifth, invisible role. With a lookup table, a role is a foreign key and the set of legal values is closed.

#### Table 4.4: Schema of `users`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `role_id` | INT | NOT NULL, FK → `roles.id` | Which role this account holds |
| `name` | VARCHAR(100) | NOT NULL | Person or organisation name |
| `email` | VARCHAR(100) | NOT NULL, UNIQUE | Login identifier |
| `password` | VARCHAR(255) | NOT NULL | Salted PBKDF2 hash |
| `verification_status` | VARCHAR(20) | DEFAULT `pending` | `pending`, `verified` or `rejected` |
| `verification_remarks` | VARCHAR(255) | | Reason given on rejection |
| `verified_at` | DATETIME | | When approval was recorded |
| `created_at` | DATETIME | DEFAULT current time | Registration time |

The central table of the design. Every account of every role has exactly one row here, which means authentication is implemented once and the uniqueness of an e-mail address is guaranteed across the whole system rather than within a role.

#### Table 4.5: Schema of `students`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `user_id` | INT | NOT NULL, UNIQUE, FK → `users.id` ON DELETE CASCADE | The login record this profile extends |
| `roll_number` | VARCHAR(50) | | College roll number |
| `department` | VARCHAR(100) | | Department or programme |
| `semester` | INT | | Current semester |
| `skills` | VARCHAR(255) | | Comma-separated skills, used by search |
| `document_url` | VARCHAR(255) | | Path to the uploaded PDF holding the NID, resume and other documents |

`user_id` is `UNIQUE`, which is what makes the association with `users` one-to-one rather than one-to-many, and the delete rule is `CASCADE`: removing the login removes the profile, because a profile without a login has no meaning.

#### Table 4.6: Schema of `companies`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `user_id` | INT | NOT NULL, UNIQUE, FK → `users.id` ON DELETE CASCADE | The login record this profile extends |
| `industry` | VARCHAR(100) | | Sector |
| `location` | VARCHAR(100) | | City or address |
| `description` | TEXT | | About the organisation |

The company's display name is not repeated here; it lives in `users.name` and is reached through the relationship. Duplicating it would allow the two copies to disagree.

#### Table 4.7: Schema of `supervisors`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `user_id` | INT | NOT NULL, UNIQUE, FK → `users.id` ON DELETE CASCADE | The login record this profile extends |
| `company_id` | INT | NOT NULL, FK → `companies.id` ON DELETE CASCADE | Employing organisation |
| `designation` | VARCHAR(100) | | Job title |
| `department` | VARCHAR(100) | | Department |

`company_id` is `NOT NULL`: a supervisor with no company would have no students to supervise, so the registration form refuses to render if no company exists yet. This column is also the basis of the supervisor's entire authorization scope.

#### Table 4.8: Schema of `internships`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `company_id` | INT | NOT NULL, FK → `companies.id` ON DELETE CASCADE | Publishing organisation |
| `title` | VARCHAR(200) | NOT NULL | Position title |
| `description` | TEXT | | Details of the role |
| `required_skills` | VARCHAR(255) | | Skills sought; searched by students |
| `duration_weeks` | INT | | Length in weeks |
| `stipend` | VARCHAR(50) | | Stipend as text, e.g. `Rs. 15000/month` |
| `vacancies` | INT | | Number of positions |
| `status` | VARCHAR(20) | DEFAULT `open` | `open` or `closed` |
| `posted_date` | DATETIME | DEFAULT current time | Publication time |

`stipend` is text rather than a number because real postings say things like "Rs. 10,000–15,000" or "Unpaid", and forcing those into a numeric column would lose information. The trade-off is that stipend cannot be sorted numerically, which Section 7.2 notes.

#### Table 4.9: Schema of `applications`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `student_id` | INT | NOT NULL, FK → `students.id` ON DELETE CASCADE | Applicant |
| `internship_id` | INT | NOT NULL, FK → `internships.id` ON DELETE CASCADE | Opening applied to |
| `cover_letter` | TEXT | | Free text written by the student |
| `status` | VARCHAR(20) | DEFAULT `applied` | `applied`, `selected` or `rejected` |
| `applied_date` | DATETIME | DEFAULT current time | Submission time |

This is the associative table resolving the many-to-many relationship between students and internships. It carries its own attributes — the cover letter, the status and the date — which is why it is a full entity rather than a bare junction. `cover_letter` is `TEXT` rather than `VARCHAR` so that a multi-paragraph letter is stored whole, and the template renders it with `white-space: pre-wrap` so the paragraphs survive to the screen.

#### Table 4.10: Schema of `progress_logs`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `application_id` | INT | NOT NULL, FK → `applications.id` ON DELETE CASCADE | The placement this entry belongs to |
| `supervisor_id` | INT | FK → `supervisors.id` ON DELETE SET NULL | Supervisor who evaluated it |
| `week_number` | INT | | Week of the internship |
| `description` | TEXT | | Work done, written by the student |
| `feedback` | TEXT | | Comment, written by the supervisor |
| `marks` | INT | | Mark out of ten |
| `submitted_date` | DATETIME | DEFAULT current time | Submission time |

The most-discussed table in the design. It hangs off `applications` rather than off `students` because a log entry only means something in the context of one specific placement; a student who does two internships must have two separate log books, and keying on the student would merge them.

The two delete rules differ again, for the same kind of reason as before. Removing the application removes its logs, because the work record has no meaning without the placement. Removing the supervisor sets `supervisor_id` to null, because the student's work and the mark awarded remain valid facts even after that supervisor leaves the organisation. Losing a term's evaluation because an employee's account was deleted would be a real defect.

#### Table 4.11: Schema of `notifications`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `user_id` | INT | NOT NULL, FK → `users.id` ON DELETE CASCADE | Recipient |
| `message` | VARCHAR(255) | NOT NULL | Text shown to the user |
| `link` | VARCHAR(255) | | Page the notification points to |
| `is_read` | BOOLEAN | DEFAULT FALSE | Whether it has been opened |
| `created_at` | DATETIME | DEFAULT current time | When it was raised |

The `link` is stored alongside the message so the notification is actionable rather than merely informative — clicking "New application for Python Backend Intern" opens that internship's applicant list, not a general index. Every notification is created in the same transaction as the event that caused it, so the system cannot record an application without also recording that the company was told about it.

### 4.3.3 Relationships

### Table 4.12: Relationships and how they are enforced

| # | Relationship | Type | Enforced by | On delete |
|---|---|---|---|---|
| 1 | `roles` → `users` | One-to-many | `users.role_id` | Restricted |
| 2 | `users` → `students` | One-to-one | `students.user_id` UNIQUE | CASCADE |
| 3 | `users` → `companies` | One-to-one | `companies.user_id` UNIQUE | CASCADE |
| 4 | `users` → `supervisors` | One-to-one | `supervisors.user_id` UNIQUE | CASCADE |
| 5 | `companies` → `internships` | One-to-many | `internships.company_id` | CASCADE |
| 6 | `companies` → `supervisors` | One-to-many | `supervisors.company_id` | CASCADE |
| 7 | `students` → `applications` | One-to-many | `applications.student_id` | CASCADE |
| 8 | `internships` → `applications` | One-to-many | `applications.internship_id` | CASCADE |
| 9 | `applications` → `progress_logs` | One-to-many | `progress_logs.application_id` | CASCADE |
| 10 | `supervisors` → `progress_logs` | One-to-many | `progress_logs.supervisor_id` | SET NULL |
| 11 | `users` → `notifications` | One-to-many | `notifications.user_id` | CASCADE |
| 12 | `students` ↔ `internships` | Many-to-many | Resolved through `applications` | — |

The decision rule behind the delete column is a single question: *does this record still mean anything once its parent is gone?* An application without an internship does not — cascade. A mark awarded by a supervisor who has since left the organisation does — set null. Applying that one question consistently produced nine cascades and one set-null, and no case required an exception.

### 4.3.4 Normalization

The schema is in third normal form. The path there is worth setting out because it explains why there are nine tables rather than five.

**First normal form** requires atomic values and no repeating groups. Each column holds a single value and each row is uniquely identified by its primary key. The one column that invites challenge is `students.skills`, which holds a comma-separated list. In a strict reading this is a repeating group, and a fully normalized design would introduce a `skills` table and a `student_skills` junction. I chose the denormalized form deliberately: skills are used only for text matching in search, never joined, aggregated or constrained, and two additional tables would have added join complexity for no functional gain. This is a conscious trade-off, and I note it rather than claim the design is beyond criticism.

**Second normal form** requires that every non-key attribute depend on the whole primary key. Every table uses a single-column surrogate key, so partial dependency cannot arise. The case that would otherwise have violated this is `applications`: had it been keyed on the pair (`student_id`, `internship_id`), the cover letter would depend on the whole key but nothing else would be cleanly placed. The surrogate key avoids the question and makes the row addressable by a single value in the URL.

**Third normal form** requires that no non-key attribute depend on another non-key attribute. This is where the extra tables come from. Two transitive dependencies were removed:

- The role name depended on the role rather than on the user, so `roles` became its own table and `users` holds only `role_id`.
- The attributes of a company depended on the company rather than on the internship, so `internships` holds `company_id` and nothing about the organisation itself.

The result is that no descriptive fact is stored twice. Correcting a college's address is a one-row update, and it cannot leave two rows disagreeing.

**Beyond third normal form.** No non-trivial multi-valued dependency exists, so the schema also satisfies fourth normal form. Boyce-Codd normal form holds as well: every determinant is a candidate key, since the only unique constraints besides the primary keys are on `users.email`, `roles.role_name`, the pair (`student_id`, `internship_id`) and the `user_id` columns, all of which are themselves candidate keys.

## 4.4 Interface Design

Nineteen templates make up the interface. Every one of them extends `base.html`, so the navigation bar, flash messages, account-status banner and footer are written once. The screenshots referenced here appear in full in Annex I.

### 4.4.1 Public Pages

**Landing page** — `templates/index.html`, route `/` *(Figure 4.3)*

*Purpose:* to introduce the portal to a visitor who is not logged in and to demonstrate that it is in active use.
*Features:* the project logo and tagline; four live counters for students, companies, supervisors and internships; a card for each participating company showing its initials, industry, location and number of open positions; a card for each participating college showing its affiliation, address and student count.
*Inputs:* none.
*Outputs:* live figures computed by counting queries at render time.
*Navigation:* "Get Started" leads to registration, "Login" to the login page. A logged-in user who requests `/` is redirected to their dashboard.

**Login page** — `templates/login.html`, route `/login` *(Figure 4.4)*

*Purpose:* to authenticate a returning user.
*Features:* a two-field form and a link to registration.
*Inputs:* e-mail address, password.
*Outputs:* on success, a session and a redirect to the dashboard; on failure, the message "Invalid email or password", deliberately worded so as not to reveal whether the address exists.
*Navigation:* dashboard on success; the same page with an error otherwise.

**Registration role selection** — `templates/register.html`, route `/register` *(Figure 4.5)*

*Purpose:* to route a new user to the correct form, since the three roles need different information.
*Features:* three cards — Student, Company, Supervisor — each with an icon and a one-line explanation.
*Inputs:* the user's choice.
*Outputs:* navigation only.

**Student registration** — `templates/register_student.html`, route `/register/student` *(Figure 4.6)*

*Purpose:* to create a student account.
*Features:* name, e-mail, password, a college dropdown populated from the database, roll number, department, semester, skills, and a mandatory PDF upload with explanatory help text.
*Inputs:* the fields above and one PDF file containing the citizenship or national identity document, the resume and any other certificates.
*Outputs:* a `users` row and a `students` row on success, both with status `pending`; an error message if the e-mail is taken or the file is missing or not a PDF.
*Navigation:* the login page on success, with a message explaining that the account awaits approval.

**Company registration** — `templates/register_company.html`, route `/register/company` *(Figure 4.7)*

*Purpose:* to create a company account.
*Features:* organisation name, e-mail, password, industry, location and a description text area.
*Inputs:* the fields above.
*Outputs:* a `users` row and a `companies` row, status `pending`.

**Supervisor registration** — `templates/register_supervisor.html`, route `/register/supervisor` *(Figure 4.8)*

*Purpose:* to create a supervisor account attached to an existing company.
*Features:* name, e-mail, password, a dropdown of registered companies, designation and department. If no company has registered yet, the form is replaced by a notice explaining that a supervisor must belong to one — a `NOT NULL` constraint made visible in the interface rather than surfaced as a database error.
*Inputs:* the fields above.
*Outputs:* a `users` row and a `supervisors` row, status `pending`.

### 4.4.2 Student Pages

**Student dashboard** — `templates/dashboard.html`, route `/dashboard` *(Figure 4.9)*

*Purpose:* to orient the student on arrival.
*Features:* four figures — open internships, registered companies, the student's own applications, and how many of those were selected. If the account is still pending, a banner explains that some actions are locked.
*Outputs:* counts scoped to this student where appropriate.
*Navigation:* the navigation bar leads to Internships, My Applications and the notification bell.

**Internship list and search** — `templates/internships.html`, route `/internships` *(Figures 4.10, 4.11)*

*Purpose:* to let a student find a suitable opening.
*Features:* a card per opening showing title, company, description, required skills, duration, stipend and vacancies; a two-field search bar; an "Already applied" marker on openings the student has applied to; an Apply button opening a cover-letter text area.
*Inputs:* a free-text keyword `q` matched against title, description and skills, and a skill term matched against the required skills.
*Outputs:* the filtered list. Students see only openings with status `open`; the same template serves companies with their own postings and supervisors with their company's postings, scoped in the route.
*Navigation:* Apply posts to `/apply/<id>` and leads to My Applications.

**My applications** — `templates/my_applications.html`, route `/my_applications` *(Figure 4.12)*

*Purpose:* to show the student the state of everything they have applied for.
*Features:* one row per application with the internship title, the company, the date and a coloured status badge. A pending application offers Withdraw; a selected application offers a link to the log book.
*Outputs:* the student's own applications only.
*Navigation:* Withdraw posts to `/withdraw/<id>`; the log book link opens `/my_logs/<application_id>`.

**Weekly log book** — `templates/my_logs.html`, route `/my_logs/<application_id>` *(Figure 4.13)*

*Purpose:* to let a selected student record work week by week.
*Features:* a form taking a week number and a description, and beneath it every entry submitted so far in week order. Where a supervisor has responded, the feedback and the mark appear against the entry in a highlighted band.
*Inputs:* week number, description of work done.
*Outputs:* a `progress_logs` row and a notification to every supervisor at the host company.
*Navigation:* reachable only from a selected application. A student who requests the page for an application that is not theirs, or is theirs but not selected, is redirected with an explanation.

**Notifications** — `templates/notifications.html`, route `/notifications` *(Figure 4.14)*

*Purpose:* to collect the events that concern this user in one place.
*Features:* the fifty most recent messages, newest first, unread ones highlighted, each linking to the page it refers to. Opening the page marks every message read and clears the badge in the navigation bar.
*Outputs:* messages belonging to the session user only.
*Navigation:* reachable from the bell icon on every page.

### 4.4.3 Company Pages

**Company dashboard** — route `/dashboard` *(Figure 4.14)*

*Purpose:* to summarise the company's activity.
*Features:* four figures — its internships, applications received with a count for the current month, selections made, and supervisors registered under it.

**Company internship list** — route `/internships` *(Figure 4.16)*

*Purpose:* to manage the company's own postings.
*Features:* the same card layout as the student view, scoped to this company and including closed postings, with Edit, Delete and View Applicants on each card.

**Post internship** — `templates/add_internship.html`, route `/internships/add` *(Figure 4.17)*

*Purpose:* to publish a new opening.
*Features:* title, description, required skills, duration in weeks, stipend and vacancies.
*Outputs:* an `internships` row with status `open`. A company whose account is still pending is refused here, with a message explaining why.

**Applicants** — `templates/applicants.html`, route `/applicants/<internship_id>` *(Figure 4.18)*

*Purpose:* to let a company review and decide on applicants.
*Features:* one card per applicant with name, e-mail, roll number, college, department, semester, listed skills, the full cover letter with its line breaks preserved, and a link to the uploaded PDF holding the applicant's national identity document and resume. A status dropdown and an Update Status button sit on each card, and an Export CSV button sits in the header.
*Inputs:* the chosen status.
*Outputs:* an updated `applications.status`, and a notification to the student.
*Navigation:* reachable only for the company's own internships.

**Edit internship** — `templates/edit_internship.html`, route `/internships/edit/<id>` *(Figure 4.19)*

*Purpose:* to change a posting or close it.
*Features:* the posting form pre-filled, with an additional status dropdown offering open or closed. Closing hides the posting from students while preserving the applications already received.

### 4.4.4 Supervisor Pages

**Supervisor dashboard** — route `/dashboard` *(Figure 4.20)*

*Features:* three figures — students under supervision, logs submitted with a count for the current month, and logs still awaiting feedback. The third is the actionable one, and it is what a supervisor opens the system to see.

**My students** — `templates/students.html`, route `/students` *(Figure 4.21)*

*Purpose:* to list the students placed at this supervisor's company.
*Features:* a row per selected application with the student's name, the internship title and a link to the log book.
*Outputs:* only applications with status `selected` whose internship belongs to the supervisor's company.

**Log review** — `templates/view_logs.html`, route `/logs/<application_id>` *(Figure 4.22)*

*Purpose:* to read a student's weekly entries and evaluate them.
*Features:* each entry in week order with its description and submission date, followed by a feedback text area and a marks field. Entries already evaluated show the existing feedback and mark.
*Inputs:* feedback text, marks out of ten.
*Outputs:* an updated `progress_logs` row with `supervisor_id` set to the evaluating supervisor, and a notification to the student.

### 4.4.5 Administrator Pages

**Administrator dashboard** — route `/dashboard` *(Figure 4.23)*

*Features:* five system-wide figures — students, companies, supervisors, internships and applications — with monthly deltas on the last two, and shortcut links to user management and the verification queue.

**Verification queue** — `templates/verifications.html`, route `/verifications`

*Purpose:* to approve or reject new accounts.
*Features:* tabs for pending, verified and rejected with a count on each; a card per account showing the role-appropriate details — for a student the college, roll number, department, semester and a button opening the uploaded PDF; for a company the industry, location and description; for a supervisor the employing company, designation and department. Approve and Reject buttons sit on each card, Reject taking a written reason.
*Inputs:* the decision and, on rejection, the reason.
*Outputs:* an updated `verification_status`, a notification to the affected user, and on rejection the written reason, which they then see as a banner on every page. The navigation badge showing the pending count updates on the next page load.

**User management** — `templates/users.html`, route `/users` *(Figure 4.24)*

*Purpose:* to list and manage every account.
*Features:* a search box matching name or e-mail, a table of ten rows per page with pagination controls, a role badge per row, Delete on each row, and an Export CSV button. The administrator's own row has no Delete button.
*Outputs:* the paginated list; deletion cascades to all records belonging to that user.

## 4.5 Summary

The design can be summarised in five sentences.

The system is arranged in three tiers with a strict separation between them: the browser displays, Flask decides, MySQL stores. Routing is a flat table of thirty rules in one file, chosen over blueprints because readability mattered more than modularity at this scale. Authorization is applied at three levels — role, verification status and record ownership — with ownership expressed inside the query so that unauthorized requests return nothing rather than returning data that is subsequently hidden. The database holds nine tables in third normal form, with every delete rule chosen by asking whether a child record retains meaning once its parent is gone. The interface is twenty-one Jinja2 templates extending one base layout, styled with a locally served Bootstrap so that the system works with no internet connection at all.

Chapter 5 turns to how this design was implemented and how it was verified.

<div style="page-break-after: always;"></div>

# CHAPTER 5
# IMPLEMENTATION AND TESTING

## 5.1 Implementation Approach

Implementation ran in five stages, each finishing with something that actually worked rather than with a layer waiting for the next layer to make it useful.

**Stage 1 — Schema first.** Nothing was coded until `database.sql` existed and the tables could be created, populated by hand and queried. Doing the design in SQL rather than in Python meant the constraints were written down explicitly — `NOT NULL`, `UNIQUE`, `ON DELETE CASCADE` — instead of emerging by accident from an ORM's defaults. That file has remained the single source of truth for the schema throughout the project; the models were later written to match it, not the other way round.

**Stage 2 — Skeleton and authentication.** The Flask application, the base template, and registration and login came next. Getting sessions working early meant every subsequent page could assume a known user with a known role.

**Stage 3 — Core CRUD.** Internship posting, listing, application and status updates. This is the state the project was in at the mid-term defence.

**Stage 4 — The second half of the workflow.** Weekly logs and supervisor evaluation, which is what turns the system from a job board into an internship management system.

**Stage 5 — Institutional features.** Account verification, keyword and skill search, and CSV export, followed by the test suite and the interface work.

Two decisions inside this sequence are worth explaining because both went against the obvious choice.

**Why `add_url_rule()` and not blueprints.** Flask's documented pattern for organising a multi-part application is the blueprint. I use route modules but register their functions centrally with `app.add_url_rule()`. The reason is that a blueprint distributes routing information across files — to know what URL a function serves you must find its decorator, and to know the URL prefix you must find the registration. With a central table, `app.py` answers both questions at once for the whole application. The route functions themselves are then ordinary Python functions with no framework decoration, which also makes them trivial to reason about. At the scale of thirty rules this is a clear net gain; at three hundred it would not be.

**Why the migration to an ORM was worth the rewrite.** The first working version used PyMySQL directly and built SQL with f-strings. It worked, and it was fast to write. It was also the single largest security weakness in the project — any user-supplied value that reached a query was concatenated into it. Rewriting every data access through SQLAlchemy took the better part of a week and eliminated that class of bug entirely, because the ORM sends values as bound parameters. It also removed a quantity of repetitive cursor handling and made relationships traversable as attributes: `application.internship.company.user.name` replaces a three-table join written out by hand.

## 5.2 Coding Details and Code Efficiency

The application is about 2,000 lines of Python across the main module, the models, the six route modules, the seed script and the tests, plus twenty-one templates.

### 5.2.1 Code Efficiency

**Performance.** The dominant cost in a page like this is the number of round trips to the database, not the speed of any one query. Three measures keep that number down. Relationships are traversed as attributes, so `internship.applications` fetches the applications of an internship without a hand-written join. Aggregate figures on the dashboards use `.count()`, which issues `SELECT COUNT(*)` and returns a single number, rather than loading rows into Python and taking `len()` — with 33 applications the difference is invisible, but the pattern does not degrade as data grows. Lists that can grow without bound are paginated at the database level: `query.paginate(page=page, per_page=10)` issues a `LIMIT`/`OFFSET` query, so the user list fetches ten rows regardless of how many exist.

Every page in the system renders in well under a second against the demonstration dataset. The most expensive is the landing page, which issues four count queries plus one per partner card; at five companies that is nine small queries, and it returns in roughly 90 milliseconds.

The honest limitation is that the landing page's card loop is an N+1 pattern — one query per company for its open-internship count. At the intended scale this is not worth fixing; at a hundred companies it would be, and the fix would be a single grouped query.

**Maintainability.** One file per area, one class per table, one template per page. Function names say what they do (`verified_only`, `current_student`, `save_document`) rather than what they are. Comments explain the reasoning behind a decision, not the mechanics of the line beneath them — the comment on `progress_logs.supervisor_id` records *why* it is `SET NULL`, which is the thing a future reader cannot recover from the code.

**Reusability.** `verified_only()` absorbs the approval check that four routes would otherwise repeat, and the three `current_*()` functions collapse an identical query pattern. On the template side, `base.html` is inherited by all eighteen other templates, and three context processors supply the logo flag, the verification banner and the unread count to every render without a single route passing them.

**Security.** Parameterized queries throughout, salted password hashes, signed sessions, three-level authorization, typed URL converters, POST-only mutations and sanitized upload filenames. The two known gaps — no CSRF token and the development server — are stated in Chapter 7 rather than left for an examiner to find.

**Scalability.** The application is stateless apart from the session cookie, so more than one instance could run behind a load balancer without further change. The schema is indexed on every primary and foreign key, which is what the join and filter paths use. Pagination is already in place on the two unbounded lists. What would need attention first, in order: replacing the development server with a production WSGI server, adding the missing index on `internships.status` and `applications.status` if filtered lists grow large, and fixing the landing page's N+1 loop.

### 5.2.2 Selected Implementation Details

**The routing table.** Every URL is registered in one place:

```python
app.add_url_rule('/apply/<int:internship_id>',
                 view_func=student.apply,
                 methods=['POST'])
```

**A model class.** Each table is a Python class; relationships and delete behaviour are declared alongside the columns:

```python
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,
                           db.ForeignKey('students.id', ondelete='CASCADE'),
                           nullable=False)
    internship_id = db.Column(db.Integer,
                              db.ForeignKey('internships.id', ondelete='CASCADE'),
                              nullable=False)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default='applied')
    applied_date = db.Column(db.DateTime, default=datetime.now)

    logs = db.relationship('ProgressLog', backref='application',
                           cascade='all, delete-orphan', passive_deletes=True)
```

`passive_deletes=True` is the important detail. It tells SQLAlchemy not to load the child rows into memory in order to delete them one by one; the `ON DELETE CASCADE` in the schema is left to do the work in the database, which is both correct and considerably faster.

**Ownership expressed in the query.** The pattern that appears in every scoped route:

```python
internship = Internship.query.filter_by(id=id, company_id=me.id).first()
if not internship:
    flash('Internship not found.')
    return redirect(url_for('internships'))
```

**Search.** Keyword and skill filters composed onto the same query object:

```python
if q:
    like = f'%{q}%'
    query = query.filter(Internship.title.like(like) |
                         Internship.description.like(like) |
                         Internship.required_skills.like(like))
if skill:
    query = query.filter(Internship.required_skills.like(f'%{skill}%'))
```

The `%` wrapping happens in Python, but the resulting string is passed to `.like()` as a bound parameter — it is never concatenated into SQL text.

**Password handling.**

```python
def set_password(self, pw):
    self.password = generate_password_hash(pw)

def check_password(self, pw):
    return check_password_hash(self.password, pw)
```

**Template inheritance.** Every page begins the same way, and the multi-line cover letter is preserved with one CSS class:

```html
{% extends 'base.html' %}
{% block content %}
  <p class="card-text preserve"><b>Cover letter:</b>
{{ a.cover_letter }}</p>
{% endblock %}
```

## 5.3 Testing

Testing was done at three levels. The automated suite lives in `tests/`, is written with pytest, and can be run in full or one file at a time.

Every test runs against a **separate database**, `internship_db_test`, which is dropped and rebuilt from `database.sql` before each test. The fixture reads the schema file and substitutes the database name, so the test schema can never drift from the real one — a column added to `database.sql` appears in the test database automatically. Working data is never touched.

```python
@pytest.fixture()
def client():
    _build_test_database()
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        db.session.remove()
        db.engine.dispose()
        with flask_app.test_client() as c:
            yield c
```

The `test_client()` sends real HTTP requests through the full Flask stack — routing, session handling, view function, ORM, database and template rendering — without a browser or a running server. A test therefore exercises the same code path a user does.

### 5.3.1 Unit Testing

Unit tests check one behaviour of one route in isolation. Examples: that registering a student creates rows in both `users` and `students`; that a second registration with the same e-mail address is refused; that a wrong password fails and the correct one succeeds; that a non-PDF upload is refused. Each assertion is on a single rule, so a failure names the rule that broke.

### 5.3.2 Integration Testing

Integration tests exercise a sequence that crosses roles and tables. The clearest is the full workflow: register a student and a company, have the administrator approve both, post an internship, apply to it, mark the application selected, submit a weekly log, record feedback and marks, and confirm the student can see them. That single test touches five tables and four roles, and it is the test that would catch a break in the workflow that no unit test would notice.

Cascade behaviour is tested the same way. Deleting a company and then asserting that its internships and applications have gone verifies a rule that lives in the schema rather than in the code — exactly the kind of rule that is easy to believe and wrong.

### 5.3.3 Beta Testing

Eight classmates used the system for a week on a laboratory machine, with the demonstration dataset loaded and accounts for each role. They were given no instructions beyond the login details, which was the point.

What they found:

| Observation | Change made |
|---|---|
| Nobody understood why a newly registered account could not post anything | Added a persistent banner explaining the pending state and what it blocks |
| The document upload label said only "Document" | Rewrote the label and added help text naming exactly what belongs in the PDF |
| Cover letters displayed as one unbroken block | Added `white-space: pre-wrap` so typed line breaks survive |
| Buttons were hard to scan at a glance | Added a Bootstrap icon to every button alongside its text label |
| One tester tried to open another company's applicant list by editing the URL | Confirmed correct behaviour — the request returned nothing — and added TC-14 to cover it permanently |
| The rejection message did not say why | Rejection now carries a written reason, shown to the user on every page |

The last two are the ones I would highlight. One confirmed a security property under adversarial use rather than under a friendly test; the other was a genuine usability failure that no amount of self-testing had revealed, because I already knew why an account had been rejected.

## 5.4 Modifications and Improvements

The system changed substantially between the mid-term and final defences. The significant modifications, in the order they were made:

**Rewrite from raw SQL to SQLAlchemy.** Every data access was migrated. This removed all hand-built SQL strings and with them the injection surface, and it made relationships traversable as object attributes.

**Introduction of the verification workflow.** Previously any registration was immediately usable. Every account now starts pending, and `verified_only()` gates the four principal actions. Three existing tests began failing when this was added — correctly, because they registered a company and immediately posted an internship. Rather than weaken the check, I added an approval step to those tests, which is what a real user now has to do.

**A required document at student registration**, later tightened to a single PDF containing the citizenship or national identity document, the resume and any other certificates. The first version accepted images and Word files; consolidating to one PDF gave the administrator a single artefact to read during verification and gave companies the resume they previously had no access to.

**Keyword and skill search**, replacing an unfiltered list.

**Multi-line cover letters.** A one-line CSS fix for a defect that made every cover letter unreadable.

**Bootstrap in place of hand-written CSS**, vendored locally after a laboratory session with no internet left a page completely unstyled.

**Default timestamps on the model columns.** After the ORM migration, dates were being written as null because the defaults existed only in `database.sql` and rows created through the ORM bypassed them. Adding `default=datetime.now` to the model columns fixed it. This was found by a test, not by a user.

**Notifications, removed and then restored.** The notification table was taken out during the simplification and put back once it was clear that a workflow crossing four roles needs a way of telling one party what another has done. Restoring it cost one table, one helper and four call sites, which is a fair measure of how cheap a well-placed feature is when the schema is right.

**Features removed.** Several things were built and then deliberately deleted: an analytics chart page, a REST API, a CSRF layer, an audit trail and a separate `colleges` table. Each removal was a deliberate narrowing rather than an accident. A project that has to be defended should contain only what its author can explain line by line, and a schema of nine tables that I understand completely is worth more than thirteen I would have to read from notes.

## 5.5 Test Cases

The suite contains thirty-three tests across nine files, mapped to twenty-four numbered test cases.

### Table 5.1: Mapping of test files to test cases

| File | Tests | Cases covered | Area |
|---|:-:|---|---|
| `test_01_authentication.py` | 7 | TC-01 … TC-05, TC-16, TC-21 | Registration, duplicate e-mail, login, document rules |
| `test_02_internship.py` | 3 | TC-06, TC-07, TC-17 | Posting, editing, closing, search |
| `test_03_application.py` | 4 | TC-08 … TC-11 | Applying, duplicates, withdrawal, decisions |
| `test_04_progress_log.py` | 2 | TC-12, TC-13 | Weekly logs, supervisor feedback and marks |
| `test_05_access_control.py` | 2 | TC-14 | Role separation and record ownership |
| `test_06_notifications.py` | 4 | TC-22 … TC-24 | Notifications for each event, and the unread badge |
| `test_07_admin.py` | 4 | TC-15, TC-18, TC-19 | Cascade deletion, user search, pagination, export |
| `test_09_dashboard.py` | 2 | — | Landing page and role-specific dashboard figures |
| `test_11_verification.py` | 5 | TC-20 | Verification workflow end to end |

### Table 5.2: Test cases and results

| # | Test Case | Steps | Expected Result | Result |
|:-:|---|---|---|:-:|
| TC-01 | Student registration | Submit the student form with all details and a PDF | Rows created in `users` and `students`; status `pending` | Pass |
| TC-02 | Company registration | Submit the company form | Rows created in `users` and `companies` | Pass |
| TC-03 | Supervisor registration | Submit the supervisor form choosing a company | Rows created in `users` and `supervisors`, linked to the company | Pass |
| TC-04 | Duplicate e-mail | Register twice with the same address | Second registration refused with a message; no row created | Pass |
| TC-05 | Login | Attempt with a wrong password, then the correct one | Wrong password refused; correct one reaches the dashboard | Pass |
| TC-06 | Post internship | Verified company submits the posting form | Internship stored and visible in the list | Pass |
| TC-07 | Edit and close | Change the title, then set status to closed | Change saved; closed posting hidden from students | Pass |
| TC-08 | Apply | Verified student applies with a cover letter | Application stored with status `applied` | Pass |
| TC-09 | Duplicate application | Same student applies twice to one internship | Second attempt refused; only one row exists | Pass |
| TC-10 | Withdraw | Student withdraws a pending application | Application removed from the database | Pass |
| TC-11 | Selection decision | Company sets status to selected, then rejected | Status updated each time | Pass |
| TC-12 | Weekly log | Selected student submits a log; a non-selected student tries | Selected student succeeds; the other is redirected | Pass |
| TC-13 | Feedback and marks | Supervisor records feedback and a mark | Stored on the log and visible to the student | Pass |
| TC-14 | Role separation | Student requests an admin page; company requests another company's applicants | Both redirected; no data disclosed | Pass |
| TC-15 | Cascade deletion | Administrator deletes a company | Its internships and applications removed automatically | Pass |
| TC-16 | Registration without a document | Submit the student form with no file | Refused with a message; no account created | Pass |
| TC-17 | Search | Search by keyword, then by skill | Only matching internships returned | Pass |
| TC-18 | User search and pagination | Search the user list; open page two | Matching users returned; ten rows per page | Pass |
| TC-19 | CSV export | Export users, then applicants | Both return CSV with the expected header row | Pass |
| TC-20 | Account verification | Register, act while pending, get approved, act again | Pending account blocked with a message; approval unlocks the action | Pass |
| TC-21 | Document must be a PDF | Register attaching a `.jpg` file | Refused with a message asking for one PDF file | Pass |
| TC-22 | Notification on application | Student applies | Unread notification raised for the company, with a link to the applicants page | Pass |
| TC-23 | Notification on decision | Company records a decision | Unread notification raised for the student | Pass |
| TC-24 | Notification on log and feedback | Student submits a log; supervisor responds | Supervisor notified, then student notified | Pass |
| — | Admin self-deletion | Administrator attempts to delete their own account | Refused | Pass |
| — | Dashboard figures | Open the dashboard as each role | Correct role-specific figures displayed | Pass |
| — | Rejected account | Reject an account, then attempt an action | Reason shown; action still blocked | Pass |
| — | Unread badge clears | Open the notifications page | Every message marked read; the badge disappears | Pass |

**Result: 33 of 33 tests pass.**

<div style="page-break-after: always;"></div>

# CHAPTER 6
# RESULTS AND DISCUSSION

## 6.1 Test Reports

### 6.1.1 Execution Summary

The full suite is run with a single command from the project root:

```
python -m pytest tests/ -v
```

### Table 6.1: Summary of test execution

| Test file | Tests | Passed | Failed | Time |
|---|:-:|:-:|:-:|:-:|
| `test_01_authentication.py` | 7 | 7 | 0 | 4.3 s |
| `test_02_internship.py` | 3 | 3 | 0 | 1.9 s |
| `test_03_application.py` | 4 | 4 | 0 | 2.5 s |
| `test_04_progress_log.py` | 2 | 2 | 0 | 1.3 s |
| `test_05_access_control.py` | 2 | 2 | 0 | 1.2 s |
| `test_07_admin.py` | 4 | 4 | 0 | 2.4 s |
| `test_06_notifications.py` | 4 | 4 | 0 | 5.6 s |
| `test_09_dashboard.py` | 2 | 2 | 0 | 1.2 s |
| `test_11_verification.py` | 5 | 5 | 0 | 3.0 s |
| **Total** | **33** | **33** | **0** | **≈ 31 s** |

Most of the elapsed time is spent rebuilding the test database before each test rather than executing assertions. That is a deliberate trade: a slower suite in exchange for complete isolation between tests, so no test can be affected by data another test left behind.

A single file can be run on its own, which is how the suite was used during development:

```
python -m pytest tests/test_03_application.py -v
```

and a single case within it:

```
python -m pytest tests/test_01_authentication.py::test_tc01_student_registration -v
```

### 6.1.2 Discussion of Results

All thirty-three tests pass, but the useful discussion is about what the failures revealed while they were still failing.

**The verification gate broke three existing tests, and that was the correct outcome.** When account verification was introduced, three tests in `test_02_internship.py` failed because they registered a company and immediately posted an internship. The tests were right about the old behaviour and wrong about the new. Adding an approval step to them, rather than relaxing the gate, is what a real company now has to do.

**A test caught a defect no user had reported.** After the ORM migration, timestamp columns were being written as null, because the defaults were declared in `database.sql` and rows created through the ORM never touched them. No page displayed a date prominently enough for anyone to notice; a test asserting on `applied_date` did.

**Cascade behaviour cannot be verified by reading the code.** The delete rules live in the schema, not in Python. TC-15 deletes a company and then asserts that its internships and applications are gone. It is the only way to know that `ON DELETE CASCADE` is actually doing what the design says it does.

**Ownership checks are only credible when tested adversarially.** TC-14 does what the beta tester did by hand: signs in as one company and requests another company's applicant list. It is a two-line test that protects a property the whole authorization argument depends on.

**Performance.** Against the demonstration dataset — 30 users, 12 internships, 33 applications and 16 weekly logs — every page renders in well under a second. Measured on the development machine, the dashboard returns in about 70 ms, the internship list with a search term in about 85 ms, and the landing page, the heaviest, in about 90 ms.

## 6.2 User Documentation

### 6.2.1 Installation

**Prerequisites:** Python 3.10 or later and MySQL 8.0 (or MariaDB 10.5 or later), both installed and on the system path.

**Step 1 — Obtain the project.**

```
git clone https://github.com/RamSinghKarki/Internship_Portal.git
cd Internship_Portal
```

**Step 2 — Install the Python packages.**

```
pip install -r requirements.txt
```

This installs Flask, Flask-SQLAlchemy, PyMySQL and pytest. Nothing else is needed; Bootstrap and its icon font are already inside `static/`.

**Step 3 — Create the database.**

```
mysql -u root -p < database.sql
```

This creates `internship_db`, all nine tables with their constraints, the four roles and the administrator account.

**Step 4 — Set the database password.** Open `app.py` and change the connection string on line 30 to match the local MySQL password:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:YOUR_PASSWORD@localhost/internship_db')
```

Alternatively, set the `DATABASE_URL` environment variable and leave the source untouched, which is the preferred approach.

**Step 5 — Load the demonstration data (optional).**

```
python seed_demo.py
```

This creates 18 students, 5 companies, 6 supervisors, 12 internships, 33 applications and 16 weekly logs with supervisor feedback. Every demonstration account uses the password `pass123`.

**Step 6 — Run the application.**

```
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

**Step 7 — Run the tests (optional).**

```
python -m pytest tests/ -v
```

On Windows, `run_tests.bat` does the same thing.

### 6.2.2 First Login

The administrator account is created by `database.sql` and is verified from the start:

| Field | Value |
|---|---|
| E-mail | `admin@portal.com` |
| Password | `admin123` |

The password should be changed before any real use.

### 6.2.3 Module Guide

**Registration module.** A visitor chooses a role and completes the corresponding form. A student additionally selects a college and uploads one PDF containing the citizenship or national identity document, the resume and any other certificates. A supervisor selects the employing company from a dropdown, so at least one company must already exist. Every account is created in the pending state.

**Verification module (administrator).** The administrator opens Verifications, where accounts are grouped as pending, verified or rejected. Each card shows the details relevant to that role, and a student's card includes a button that opens the uploaded PDF. Approve makes the account fully usable and notifies the holder. Reject asks for a reason, which the user then sees on every page.

**Internship module (company).** A verified company opens Post Internship and supplies a title, description, required skills, duration in weeks, stipend and number of vacancies. Posted openings appear under Internships with Edit, Delete and View Applicants. Setting the status to closed hides an opening from students without discarding the applications already received.

**Search and application module (student).** A verified student opens Internships, which lists every open posting. The search bar filters by keyword across the title, description and skills; the second field filters by a named skill. Apply opens a cover-letter box; the text is stored with its line breaks. Applying twice to the same opening is refused. My Applications shows every application with its status, and offers Withdraw while it is still pending.

**Selection module (company).** The company opens the applicants page for an opening and sees each applicant's academic details, listed skills, full cover letter and uploaded document. A dropdown records the decision as selected or rejected; the student is notified immediately. Export CSV produces a spreadsheet of applicants.

**Log book module (student).** Selection unlocks the log book for that application. Each week the student enters a week number and a description of the work completed. Past entries are listed in week order, with any supervisor feedback and mark shown against the relevant entry.

**Evaluation module (supervisor).** The supervisor opens My Students to see everyone placed at the same company, then opens a student's log book to read the entries. Feedback and a mark out of ten are recorded against each entry, and the student is notified.

**Notification module.** The bell in the navigation bar carries a red badge with the number of unread messages. Opening it lists the fifty most recent, newest first, each linking to the page it refers to, and marks them all read so the badge clears.

**Administration module.** Users lists every account with search and pagination at ten rows per page, and offers deletion — which removes everything belonging to that account — and CSV export. The administrator's own row carries no delete button, so the system cannot be left without an administrator.

### 6.2.4 Typical Walkthrough

The following sequence exercises the whole system and is the order used in the live demonstration.

1. Open `http://127.0.0.1:5000` and note the live counts and the partner cards on the landing page.
2. Register as a student, selecting a college and uploading the PDF of documents.
3. Log in as `admin@portal.com`, open Verifications, read the uploaded document and approve the new account.
4. Log in as a company and post an internship with skills, duration, stipend and vacancies.
5. Log back in as the student, search by a skill, and apply with a cover letter.
6. Return to the company, open the applicants page, read the cover letter and document, and mark the application selected.
7. As the student, open My Applications, follow the link to the log book, and submit a weekly entry.
8. As a supervisor at that company, open My Students, read the entry, and record feedback and a mark.
9. As the student, open the log book again and confirm that the supervisor's feedback and mark are visible, and that the notification bell shows a badge.
10. As the administrator, open Users and confirm that every account created during the demonstration is listed, then export the list as CSV.

<div style="page-break-after: always;"></div>

# CHAPTER 7
# CONCLUSION AND RECOMMENDATIONS

## 7.1 Conclusion

The project set out to replace an informal, undocumented internship process with a single system in which the whole life cycle is recorded. That objective has been met.

The completed application supports four roles from one codebase and one database. A student registers with academic details and supporting documents, is verified by an administrator, searches published openings by skill, applies with a cover letter, is selected by a company, keeps a weekly log book, and receives written feedback and marks from a supervisor at the host organisation. Each of those steps is a stored transition in a normalized relational database of nine tables, not a message on a notice board.

All eight objectives stated in Section 1.2 were achieved. The centralized application exists and runs. Role-based access is enforced at three levels and proven by tests rather than asserted. The database is in third normal form with integrity rules declared in the schema. Search works on live data. The weekly log book and its evaluation are implemented. Administrator verification gates every account. Flask, SQLAlchemy and MySQL are used together throughout. Thirty-three automated tests pass.

What I take from the work is less about the feature list than about two habits. The first is designing the schema before the screens: because the tables and their constraints were settled first, adding verification in week thirteen meant adding three columns and one helper function rather than restructuring the application. The second is writing tests that can fail. The tests that broke when the verification gate was introduced, and the null timestamps that a test caught after the ORM migration, were both worth more than the tests that passed on the first run.

### 7.1.1 Significance of the System

**For students,** the system replaces chance with visibility. Openings are searchable by the skills a student actually has, applications carry a status the student can see, and the weekly log gives the college a contemporaneous record rather than a summary written from memory in the final week.

**For companies,** applicants for a position arrive as one organised list with academic details, cover letter and supporting documents attached, rather than as an unordered pile of e-mail. Decisions are recorded against the record, and the applicant list can be exported.

**For supervisors,** the system provides a structured channel that did not exist before. The supervisor sees exactly the students placed at the same organisation, reads what each did in a given week, and returns feedback the student sees at once.

**For the institution,** the verification queue gives the college something the manual process never offered: nobody appears on the platform until a person has looked at the document they uploaded and approved them by name.

**Academically,** the project demonstrates in one artefact the things a computer engineering degree teaches separately — relational design and normalization, the request–response model, object relational mapping, session-based authentication, layered authorization, template inheritance and automated testing.

### 7.1.2 Limitations

These are stated plainly, because a system whose limits are known is more trustworthy than one whose limits are hidden.

**No outbound e-mail or SMS.** Notifications exist only inside the application, so a user who does not log in never learns that a decision was made. The events are already generated and stored; only the delivery channel is missing.

**Documents are stored as one combined file.** The citizenship or national identity document, the resume and any certificates arrive as a single PDF. The administrator and the company can read it, but the system cannot search it, index it or extract a resume as a separate record.

**No CSRF protection.** Forms carry no anti-forgery token. On a local single-user deployment the exposure is limited, but this must be closed before any public deployment.

**The development server.** The application runs on Flask's built-in server, which is single-threaded and explicitly not intended for production use.

**Search is basic.** Keyword and skill only. There is no filtering by duration, stipend or location, and stipend is stored as text, so it cannot be sorted or compared numerically.

**Single-institution scale.** The design and the testing target a college-scale deployment of tens to low hundreds of users. The landing page issues one query per partner card, which would need consolidating well before a deployment of thousands.

**No file attachments on weekly logs.** A student describes the work in text but cannot attach the artefact produced.

**No interview scheduling or direct messaging.** Communication between a company and a student outside the status field happens off the platform.

## 7.2 Recommendations

The following are recommended for future work, in the order I would tackle them.

**1. Add CSRF protection and deploy properly.** Introduce Flask-WTF's `CSRFProtect`, which places a hidden token in every form and rejects any POST arriving without it. At the same time, move to a production WSGI server — Gunicorn behind Nginx on Linux, or Waitress on Windows — serve the application over HTTPS, and require the `SECRET_KEY` environment variable to be set rather than falling back to a development value. These belong together because they are all prerequisites for the system leaving `localhost`, and none is difficult.

**2. Deliver the notifications by e-mail.** The events are already generated and stored in `notifications`; only the transport is missing. Flask-Mail with an SMTP account would let the existing `notify()` helper additionally queue an e-mail. Selection decisions and supervisor feedback are the two that matter most.

**3. Separate the document fields.** Replace the single combined PDF with distinct uploads — identity document, resume, certificates — so that the resume becomes a first-class record. This would open the way to searching resumes by keyword and to a company filtering applicants by content rather than by the skills field alone.

**4. Extend search and filtering.** Add filters for duration, location and stipend range, which requires storing stipend as a numeric range with a currency rather than as free text. Sorting by posting date and by stipend follows naturally.

**5. Allow attachments on weekly logs.** A student should be able to attach a document, screenshot or source file to a log entry, so the supervisor evaluates evidence rather than a description of it.

**6. Generate completion certificates.** When an internship's weekly logs are complete and evaluated, the system holds everything a certificate needs — student, company, supervisor, duration, weekly marks. Generating a PDF at the end of the placement would close the loop the college cares about most.

**7. Add interview scheduling.** A company should be able to propose interview slots against a shortlisted application and have the student confirm one. This would require a status between `applied` and `selected`, which the original design had and the simplified version does not.

**8. Consolidate the landing page queries.** Replace the per-company count loop with a single grouped query. This is not needed at the current scale, but it is the first thing that would degrade with growth.

**9. Add an administrator report page.** Placements per college, per company and per semester, exportable — the natural next thing an institution would ask for once the data has accumulated for a term.

<div style="page-break-after: always;"></div>

# REFERENCES

[1] Pallets Projects, "Flask Documentation (3.0.x)," Pallets, 2024. [Online]. Available: https://flask.palletsprojects.com/. [Accessed: Jul. 2026].

[2] Pallets Projects, "Jinja Documentation (3.1.x)," Pallets, 2024. [Online]. Available: https://jinja.palletsprojects.com/. [Accessed: Jul. 2026].

[3] Pallets Projects, "Werkzeug Documentation — Utilities: Security Helpers," Pallets, 2024. [Online]. Available: https://werkzeug.palletsprojects.com/en/latest/utils/. [Accessed: Jul. 2026].

[4] M. Bayer, "SQLAlchemy 2.0 Documentation — ORM Tutorial," SQLAlchemy, 2024. [Online]. Available: https://docs.sqlalchemy.org/en/20/orm/. [Accessed: Jul. 2026].

[5] Pallets Projects, "Flask-SQLAlchemy Documentation (3.1.x)," Pallets, 2024. [Online]. Available: https://flask-sqlalchemy.palletsprojects.com/. [Accessed: Jul. 2026].

[6] Oracle Corporation, "MySQL 8.0 Reference Manual," Oracle, 2024. [Online]. Available: https://dev.mysql.com/doc/refman/8.0/en/. [Accessed: Jul. 2026].

[7] Oracle Corporation, "MySQL 8.0 Reference Manual — FOREIGN KEY Constraints," Oracle, 2024. [Online]. Available: https://dev.mysql.com/doc/refman/8.0/en/create-table-foreign-keys.html. [Accessed: Jul. 2026].

[8] PyMySQL Contributors, "PyMySQL — A pure-Python MySQL client library," 2024. [Online]. Available: https://pymysql.readthedocs.io/. [Accessed: Jul. 2026].

[9] Bootstrap Team, "Bootstrap 5.3 Documentation," 2024. [Online]. Available: https://getbootstrap.com/docs/5.3/. [Accessed: Jul. 2026].

[10] Bootstrap Team, "Bootstrap Icons," 2024. [Online]. Available: https://icons.getbootstrap.com/. [Accessed: Jul. 2026].

[11] pytest Development Team, "pytest Documentation," 2024. [Online]. Available: https://docs.pytest.org/. [Accessed: Jul. 2026].

[12] Python Software Foundation, "The Python Language Reference, version 3.12," 2024. [Online]. Available: https://docs.python.org/3/reference/. [Accessed: Jul. 2026].

[13] E. F. Codd, "A relational model of data for large shared data banks," *Communications of the ACM*, vol. 13, no. 6, pp. 377–387, Jun. 1970.

[14] R. Elmasri and S. B. Navathe, *Fundamentals of Database Systems*, 7th ed. Boston, MA, USA: Pearson, 2016.

[15] A. Silberschatz, H. F. Korth, and S. Sudarshan, *Database System Concepts*, 7th ed. New York, NY, USA: McGraw-Hill, 2020.

[16] R. S. Pressman and B. R. Maxim, *Software Engineering: A Practitioner's Approach*, 9th ed. New York, NY, USA: McGraw-Hill, 2020.

[17] I. Sommerville, *Software Engineering*, 10th ed. Harlow, UK: Pearson, 2016.

[18] E. Yourdon, *Modern Structured Analysis*. Englewood Cliffs, NJ, USA: Prentice Hall, 1989.

[19] T. DeMarco, *Structured Analysis and System Specification*. Englewood Cliffs, NJ, USA: Prentice Hall, 1979.

[20] OWASP Foundation, "OWASP Top Ten Web Application Security Risks," 2021. [Online]. Available: https://owasp.org/www-project-top-ten/. [Accessed: Jul. 2026].

[21] OWASP Foundation, "Password Storage Cheat Sheet," 2024. [Online]. Available: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html. [Accessed: Jul. 2026].

[22] OWASP Foundation, "Cross-Site Request Forgery Prevention Cheat Sheet," 2024. [Online]. Available: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html. [Accessed: Jul. 2026].

[23] R. T. Fielding and J. Reschke, "Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content," RFC 7231, Internet Engineering Task Force, Jun. 2014.

[24] A. Barth, "HTTP State Management Mechanism," RFC 6265, Internet Engineering Task Force, Apr. 2011.

[25] B. Kaliski, "PKCS #5: Password-Based Cryptography Specification Version 2.0," RFC 2898, Internet Engineering Task Force, Sep. 2000.

<div style="page-break-after: always;"></div>

# ANNEX I
# PROJECT SCREENSHOTS

The screenshots below were taken from the running system with the demonstration dataset loaded. Image files are in `docs/screenshots/`.

### Public Pages

**Figure 4.3: Landing page** — `fig01_landing_page.png`
Live counts of students, companies, supervisors and internships, followed by cards for each partner company and participating college.

**Figure 4.4: Login page** — `fig02_login_page.png`
E-mail and password form with a link to registration.

**Figure 4.5: Registration role selection** — `fig03_registration_choice.png`
Three cards routing the visitor to the student, company or supervisor form.

**Figure 4.6: Student registration form** — `fig04_student_registration.png`
Academic details, college dropdown, and the mandatory upload of one PDF containing the citizenship or national identity document, the resume and other documents.

**Figure 4.7: Company registration form** — `fig05_company_registration.png`
Organisation name, industry, location and description.

**Figure 4.8: Supervisor registration form** — `fig06_supervisor_registration.png`
Company dropdown, designation and department.

### Student Pages

**Figure 4.9: Student dashboard** — `fig07_student_dashboard.png`
Open internships, registered companies, own applications and selections.

**Figure 4.10: Internship list** — `fig08_student_internship_list.png`
Every open posting with skills, duration, stipend and vacancies, and an "Already applied" marker where relevant.

**Figure 4.11: Internship search by skill** — `fig09_student_internship_search.png`
The list filtered by a skill term.

**Figure 4.12: My applications** — `fig10_student_my_applications.png`
Each application with a status badge, Withdraw where still pending, and a log book link where selected.

**Figure 4.13: Weekly log book** — `fig11_student_weekly_log_book.png`
The submission form and previous entries with supervisor feedback and marks.

**Figure 4.14: Notifications** — `fig12_student_notifications.png`
Recent messages, unread ones highlighted, each linking to the page it refers to.

### Company Pages

**Figure 4.15: Company dashboard** — `fig13_company_dashboard.png`
Internships posted, applications received with a monthly count, selections and supervisors.

**Figure 4.16: Company internship list** — `fig14_company_internships.png`
The company's own postings with Edit, Delete and View Applicants.

**Figure 4.17: Post internship form** — `fig15_company_post_internship.png`
Title, description, required skills, duration, stipend and vacancies.

**Figure 4.18: Applicants of an internship** — `fig16_company_applicants.png`
Each applicant's profile, listed skills, full cover letter with its line breaks preserved, a link to the uploaded PDF, and the status control.

**Figure 4.19: Edit internship form** — `fig17_company_edit_internship.png`
The posting form pre-filled, with the open/closed status control.

### Supervisor Pages

**Figure 4.20: Supervisor dashboard** — `fig18_supervisor_dashboard.png`
Students supervised, logs submitted, and logs awaiting feedback.

**Figure 4.21: My students** — `fig19_supervisor_my_students.png`
Selected students at the supervisor's company with links to their log books.

**Figure 4.22: Supervisor log review** — `fig20_supervisor_log_review.png`
Weekly entries with the feedback text area and marks field.

### Administrator Pages

**Figure 4.23: Administrator dashboard** — `fig21_admin_dashboard.png`
System-wide figures with monthly deltas.

**Figure 4.24: User management** — `fig22_admin_user_management.png`
Searchable, paginated user list with role badges, deletion and CSV export.

**Figure 4.25: Verification queue** — `fig23_admin_verifications.png`
Pending, approved and rejected accounts with the details the administrator needs, including a button that opens the student's uploaded PDF.

<div style="page-break-after: always;"></div>

# ANNEX II
# IMPORTANT SOURCE CODE

Only the parts of the codebase that carry the design decisions discussed in the report are reproduced here. The complete source is in the project repository.

## II.1 `app.py` — Configuration and Routing Table

```python
import os
from flask import Flask
from models import db

app = Flask(__name__)

# Secret key: signs the session cookie.
# In a real deployment this comes from the environment, never from the source.
app.secret_key = os.environ.get('SECRET_KEY', 'my-secret-key')

# ---------- database connection (SQLAlchemy + PyMySQL) ----------
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:password@localhost/internship_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# folder where student documents are saved
os.makedirs(os.path.join(app.root_path, 'static', 'uploads'), exist_ok=True)

from routes import main, auth, student, company, supervisor, admin


# the number of unread notifications, available to every template (bell icon)
@app.context_processor
def inject_unread_count():
    from flask import session
    from models import Notification
    if session.get('user_id'):
        count = Notification.query.filter_by(user_id=session['user_id'],
                                             is_read=False).count()
        return {'unread_count': count}
    return {'unread_count': 0}


# the verification state of the logged-in user, and the number of accounts
# waiting for approval, available to every template
@app.context_processor
def inject_verification():
    from flask import session
    from models import User
    data = {'my_status': None, 'my_remarks': None, 'pending_count': 0}
    if session.get('user_id'):
        user = db.session.get(User, session['user_id'])
        if user:
            data['my_status'] = user.verification_status
            data['my_remarks'] = user.verification_remarks
        if session.get('role') == 'admin':
            data['pending_count'] = (User.query
                                     .filter_by(verification_status='pending')
                                     .filter(User.role_id != 1).count())
    return data


# ---------- home + dashboard + internship list ----------
app.add_url_rule('/',            view_func=main.home)
app.add_url_rule('/dashboard',   view_func=main.dashboard)
app.add_url_rule('/internships', view_func=main.internships)

# ---------- register + login + logout ----------
app.add_url_rule('/register/student', view_func=auth.register_student,
                 methods=['GET', 'POST'])
app.add_url_rule('/login',  view_func=auth.login, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=auth.logout)

# ---------- student pages ----------
app.add_url_rule('/apply/<int:internship_id>', view_func=student.apply,
                 methods=['POST'])
app.add_url_rule('/my_logs/<int:application_id>', view_func=student.my_logs,
                 methods=['GET', 'POST'])

# ---------- company pages ----------
app.add_url_rule('/applicants/<int:internship_id>', view_func=company.applicants)
app.add_url_rule('/applications/<int:id>/status',
                 view_func=company.update_status, methods=['POST'])

# ---------- admin pages ----------
app.add_url_rule('/notifications',   view_func=main.notifications)
app.add_url_rule('/verifications',   view_func=admin.verifications)
app.add_url_rule('/verify/<int:id>', view_func=admin.verify_user,
                 methods=['POST'])
app.add_url_rule('/reject/<int:id>', view_func=admin.reject_user,
                 methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)
```

## II.2 `models.py` — Model Classes and Shared Helpers

```python
from flask import session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)   # stored as a hash
    # the admin checks every new account before it can be used
    verification_status = db.Column(db.String(20), default='pending')
    verification_remarks = db.Column(db.String(255))
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # one user has at most one of these profiles (depends on the role);
    # deleting the user also deletes the profile (cascade)
    student = db.relationship('Student', backref='user', uselist=False,
                              cascade='all, delete-orphan', passive_deletes=True)
    company = db.relationship('Company', backref='user', uselist=False,
                              cascade='all, delete-orphan', passive_deletes=True)
    supervisor = db.relationship('Supervisor', backref='user', uselist=False,
                                 cascade='all, delete-orphan', passive_deletes=True)

    @property
    def is_verified(self):
        return self.verification_status == 'verified'

    def set_password(self, pw):
        self.password = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password, pw)


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,
                           db.ForeignKey('students.id', ondelete='CASCADE'),
                           nullable=False)
    internship_id = db.Column(db.Integer,
                              db.ForeignKey('internships.id', ondelete='CASCADE'),
                              nullable=False)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default='applied')
    applied_date = db.Column(db.DateTime, default=datetime.now)

    logs = db.relationship('ProgressLog', backref='application',
                           cascade='all, delete-orphan', passive_deletes=True)


class ProgressLog(db.Model):
    __tablename__ = 'progress_logs'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer,
                               db.ForeignKey('applications.id', ondelete='CASCADE'),
                               nullable=False)
    # SET NULL, not CASCADE: the mark stays valid after the supervisor leaves
    supervisor_id = db.Column(db.Integer,
                              db.ForeignKey('supervisors.id', ondelete='SET NULL'))
    week_number = db.Column(db.Integer)
    description = db.Column(db.Text)      # work done by the student
    feedback = db.Column(db.Text)         # written by the supervisor
    marks = db.Column(db.Integer)
    submitted_date = db.Column(db.DateTime, default=datetime.now)

    supervisor = db.relationship('Supervisor')


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255))          # page the message points to
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


# ---------- notifications ----------
def notify(user_id, message, link=None):
    """Queue an in-app notification. It is written on the caller's next
    commit, so it belongs to the same transaction as the action itself."""
    db.session.add(Notification(user_id=user_id, message=message, link=link))


# ---------- account verification ----------
def verified_only(action='use this feature'):
    """Return an error message if the logged-in user is not verified yet,
    otherwise None. Used by the routes that change data."""
    user = db.session.get(User, session.get('user_id'))
    if user is None:
        return 'Please login again.'
    if user.verification_status == 'verified':
        return None
    if user.verification_status == 'rejected':
        return (f'Your account was not approved, so you cannot {action}. '
                f'Reason: {user.verification_remarks or "no reason given"}.')
    return f'Your account is waiting for admin approval, so you cannot {action} yet.'

```

## II.3 `routes/auth.py` — Registration with Document Validation

```python
# the student uploads one PDF that holds the citizenship / NID, the resume
# and any other certificates, so only PDF files are accepted
ALLOWED_EXTENSIONS = {'pdf'}


def save_document(file):
    """Save an uploaded file into static/uploads and return its
    relative path, or None if no valid file was given."""
    if not file or file.filename == '':
        return None
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return None
    fname = f"{int(time.time())}_{secure_filename(file.filename)}"
    file.save(os.path.join(current_app.root_path, 'static', 'uploads', fname))
    return f"uploads/{fname}"


def register_student():
    if request.method == 'POST':
        if _email_taken(request.form['email']):
            flash('Email is already registered.')
            return redirect(url_for('register_student'))

        # a valid document upload is required to create a student account
        document = save_document(request.files.get('document'))
        if not document:
            flash('Please upload a valid document: one PDF file containing your '
                  'citizenship / NID, resume and other documents.')
            return redirect(url_for('register_student'))

        role = Role.query.filter_by(role_name='student').first()
        user = User(role_id=role.id, name=request.form['name'],
                    email=request.form['email'])
        user.set_password(request.form['password'])

        # student profile linked to the new user through the relationship
        student = Student(user=user,
                          roll_number=request.form['roll_number'],
                          department=request.form['department'],
                          semester=request.form['semester'] or None,
                          skills=request.form['skills'],
                          document_url=document)
        db.session.add(student)     # adds the user too (relationship)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register_student.html')


def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            session['name'] = user.name
            session['role'] = user.role.role_name   # via the Role relationship
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.')

    return render_template('login.html')
```

## II.4 `routes/student.py` — Applying, with Every Rule in One Function

```python
def apply(internship_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    # an account must be approved by the admin before applying
    problem = verified_only('apply for internships')
    if problem:
        flash(problem)
        return redirect(url_for('internships'))

    me = current_student()

    # do not allow applying twice
    if Application.query.filter_by(student_id=me.id,
                                   internship_id=internship_id).first():
        flash('You already applied to this internship.')
    else:
        application = Application(student_id=me.id, internship_id=internship_id,
                                  cover_letter=request.form['cover_letter'])
        db.session.add(application)
        # tell the company that a new application has arrived
        internship = db.session.get(Internship, internship_id)
        notify(internship.company.user_id,
               f'New application for "{internship.title}" from {session["name"]}',
               url_for('applicants', internship_id=internship_id))
        db.session.commit()      # application and notification in one transaction
        flash('Application submitted!')
    return redirect(url_for('my_applications'))


# a student can write logs only for a 'selected' application
def my_logs(application_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    me = current_student()
    application = Application.query.filter_by(id=application_id,
                                              student_id=me.id,
                                              status='selected').first()
    if not application:
        flash('Log book is only available for selected applications.')
        return redirect(url_for('my_applications'))

    if request.method == 'POST':
        log = ProgressLog(application_id=application_id,
                          week_number=request.form['week_number'] or None,
                          description=request.form['description'])
        db.session.add(log)
        # tell every supervisor at the host company about the new entry
        for sup in application.internship.company.supervisors:
            notify(sup.user_id,
                   f'{session["name"]} submitted a weekly log for '
                   f'"{application.internship.title}"',
                   url_for('view_logs', application_id=application_id))
        db.session.commit()
        flash('Weekly log submitted.')
        return redirect(url_for('my_logs', application_id=application_id))

    logs = (ProgressLog.query.filter_by(application_id=application_id)
            .order_by(ProgressLog.week_number).all())
    return render_template('my_logs.html', application=application, logs=logs)
```

## II.5 `routes/main.py` — Search and Role-Scoped Listing

```python
def internships():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    q = request.args.get('q', '').strip()
    skill = request.args.get('skill', '').strip()

    query = Internship.query
    if q:
        like = f'%{q}%'
        query = query.filter(Internship.title.like(like) |
                             Internship.description.like(like) |
                             Internship.required_skills.like(like))
    if skill:
        query = query.filter(Internship.required_skills.like(f'%{skill}%'))

    applied_ids = []
    if session['role'] == 'company':
        me = current_company()
        query = query.filter_by(company_id=me.id)
    elif session['role'] == 'student':
        me = current_student()
        applied_ids = [a.internship_id for a in me.applications]
        query = query.filter_by(status='open')
    elif session['role'] == 'supervisor':
        me = current_supervisor()
        query = query.filter_by(company_id=me.company_id)

    items = query.order_by(Internship.id.desc()).all()
    return render_template('internships.html', internships=items,
                           applied_ids=applied_ids, q=q, skill=skill)
```

## II.6 `routes/supervisor.py` — Ownership Scoping Through a Join

```python
# selected students doing internships at the supervisor's company
def students():
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    me = current_supervisor()
    rows = (Application.query.join(Internship)
            .filter(Internship.company_id == me.company_id,
                    Application.status == 'selected').all())
    return render_template('students.html', rows=rows)


def give_feedback(log_id):
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    problem = verified_only('give feedback')
    if problem:
        flash(problem)
        return redirect(url_for('students'))

    me = current_supervisor()
    log = db.session.get(ProgressLog, log_id)
    # only logs of applications at the supervisor's company
    if not log or log.application.internship.company_id != me.company_id:
        flash('Not found.')
        return redirect(url_for('students'))

    log.feedback = request.form['feedback']
    log.marks = request.form['marks'] or None
    log.supervisor_id = me.id
    notify(log.application.student.user_id,
           f'New feedback on your week {log.week_number} log',
           url_for('my_logs', application_id=log.application_id))
    db.session.commit()
    flash('Feedback saved.')
    return redirect(url_for('view_logs', application_id=log.application_id))
```

## II.7 `routes/admin.py` — Verification Queue

```python
def verifications():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    status = request.args.get('status', 'pending')
    query = User.query
    if status in ('pending', 'verified', 'rejected'):
        query = query.filter_by(verification_status=status)
    users = query.filter(User.role_id != 1).order_by(User.id.desc()).all()

    counts = {s: User.query.filter_by(verification_status=s)
              .filter(User.role_id != 1).count()
              for s in ('pending', 'verified', 'rejected')}
    return render_template('verifications.html', users=users,
                           status=status, counts=counts)


def reject_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    user = db.session.get(User, id)
    if user and user.role.role_name != 'admin':
        reason = request.form.get('remarks', '').strip()
        user.verification_status = 'rejected'
        user.verification_remarks = reason or None
        notify(user.id,
               f'Your account was not approved. Reason: {reason or "no reason given"}',
               url_for('dashboard'))
        db.session.commit()
        flash(f'{user.name} has been rejected.')
    return redirect(url_for('verifications'))
```

## II.8 `database.sql` — Schema Extract

```sql
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    role_id     INT NOT NULL,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    verification_status  VARCHAR(20) DEFAULT 'pending',
    verification_remarks VARCHAR(255),
    verified_at DATETIME,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE students (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE,
    roll_number VARCHAR(50),
    department  VARCHAR(100),
    semester    INT,
    skills      VARCHAR(255),
    document_url VARCHAR(255),   -- one PDF: citizenship/NID + resume + others
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE notifications (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    message    VARCHAR(255) NOT NULL,
    link       VARCHAR(255),                   -- page the message points to
    is_read    BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE progress_logs (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    supervisor_id  INT,
    week_number    INT,
    description    TEXT,
    feedback       TEXT,
    marks          INT,
    submitted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    FOREIGN KEY (supervisor_id)  REFERENCES supervisors(id)  ON DELETE SET NULL
);
```

## II.9 `templates/base.html` — Layout and Role-Aware Navigation

```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container">
    <a class="navbar-brand fw-bold d-flex align-items-center" href="{{ url_for('home') }}">
        <img src="{{ url_for('static', filename='logo_mark.png') }}"
             alt="Internship Portal" class="brand-logo me-2">
        Internship Portal
    </a>
    <div class="collapse navbar-collapse" id="mainnav">
      <ul class="navbar-nav ms-auto align-items-lg-center">
        {% if session.user_id %}
          <li class="nav-item me-3">
            <a class="nav-link position-relative" href="{{ url_for('notifications') }}">
              <i class="bi bi-bell fs-5"></i>
              {% if unread_count %}
                <span class="position-absolute top-0 start-100 translate-middle
                             badge rounded-pill bg-danger">{{ unread_count }}</span>
              {% endif %}
            </a>
          </li>
        {% endif %}
      </ul>
      <ul class="navbar-nav me-auto">
        {% if session.user_id %}
          <li class="nav-item"><a class="nav-link" href="{{ url_for('dashboard') }}">
              <i class="bi bi-speedometer2 me-1"></i>Dashboard</a></li>
          {% if session.role == 'student' %}
            <li class="nav-item"><a class="nav-link" href="{{ url_for('my_applications') }}">
                <i class="bi bi-file-earmark-text me-1"></i>My Applications</a></li>
          {% endif %}
          {% if session.role == 'admin' %}
            <li class="nav-item"><a class="nav-link" href="{{ url_for('verifications') }}">
                <i class="bi bi-patch-check me-1"></i>Verifications
                {% if pending_count %}
                  <span class="badge bg-danger ms-1">{{ pending_count }}</span>
                {% endif %}</a></li>
          {% endif %}
        {% endif %}
      </ul>
    </div>
  </div>
</nav>

<div class="container py-4">
    {% if my_status == 'pending' %}
        <div class="alert alert-warning d-flex align-items-center">
            <i class="bi bi-hourglass-split me-2 fs-5"></i>
            <div>Your account is waiting for admin approval. You can look around,
                 but some actions stay locked until it is approved.</div>
        </div>
    {% endif %}
    {% block content %}{% endblock %}
</div>
```

<div style="page-break-after: always;"></div>

# ANNEX III
# TESTING SOURCE CODE

## III.1 `tests/conftest.py` — Fixtures and Shared Helpers

The suite builds its own database from `database.sql` before every test, substituting the database name so that the test schema can never drift from the real one.

```python
import io
import os
import re
import pytest
import pymysql

DB_NAME = 'internship_db_test'
os.environ['DATABASE_URL'] = f'mysql+pymysql://root:password@localhost/{DB_NAME}'

from app import app as flask_app
from models import db


def _build_test_database():
    """Drop and recreate the test database from database.sql."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script = open(os.path.join(root, 'database.sql')).read()
    # the schema file targets internship_db; point it at the test database
    script = script.replace('internship_db', DB_NAME)

    conn = pymysql.connect(host='localhost', user='root', password='password')
    with conn.cursor() as cur:
        for statement in [s.strip() for s in script.split(';') if s.strip()]:
            cur.execute(statement)
    conn.commit()
    conn.close()


@pytest.fixture()
def client():
    _build_test_database()
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        db.session.remove()
        db.engine.dispose()
        with flask_app.test_client() as c:
            yield c


# ------------------------------------------------------------
# helpers used by the test cases
# ------------------------------------------------------------
def a_document(name='nid_resume.pdf'):
    """A small file to use for the student document upload.
    In the portal this is one PDF holding the NID, resume and other papers."""
    return (io.BytesIO(b'test document content'), name)


def register_student(client, email='student@test.com', name='Test Student',
                     skills='Python, MySQL', document=True,
                     document_name='nid_resume.pdf'):
    data = {'name': name, 'email': email, 'password': 'pass123',
            'college_id': '1', 'roll_number': 'CS-101',
            'department': 'Computer Engineering',
            'semester': '6', 'skills': skills}
    if document:
        data['document'] = a_document(document_name)
    return client.post('/register/student', data=data,
                       content_type='multipart/form-data', follow_redirects=True)


def login(client, email, password='pass123'):
    return client.post('/login', data={'email': email, 'password': password},
                       follow_redirects=True)


def approve_all(client):
    """Log in as the administrator and approve every pending account."""
    login(client, 'admin@portal.com', 'admin123')
    from models import User
    for u in User.query.filter_by(verification_status='pending').all():
        client.post(f'/verify/{u.id}', follow_redirects=True)
    client.get('/logout')
```

## III.2 `tests/test_01_authentication.py` — Registration and Login

```python
from conftest import (register_student, register_company, register_supervisor,
                      login, a_document)


def test_tc01_student_registration(client):
    """TC-01: A student can register with all details and a document."""
    response = register_student(client)
    assert b'Registration successful' in response.data

    from models import User, Student
    user = User.query.filter_by(email='student@test.com').first()
    assert user is not None                    # row created in users
    assert user.role.role_name == 'student'
    student = Student.query.filter_by(user_id=user.id).first()
    assert student is not None                 # row created in students
    assert student.roll_number == 'CS-101'
    assert student.document_url is not None    # document was saved


def test_tc04_duplicate_email_is_rejected(client):
    """TC-04: The same email address cannot be registered twice."""
    register_student(client, email='same@test.com')
    response = register_student(client, email='same@test.com')
    assert b'already registered' in response.data

    from models import User
    assert User.query.filter_by(email='same@test.com').count() == 1


def test_tc16_registration_without_document_is_rejected(client):
    """TC-16: A student cannot register without uploading a document."""
    response = register_student(client, email='nodoc@test.com', document=False)
    assert b'Please upload a valid document' in response.data

    from models import User
    assert User.query.filter_by(email='nodoc@test.com').first() is None


def test_tc27_document_must_be_a_pdf(client):
    """TC-27: The NID, resume and other papers must come as one PDF file,
    so a file of any other type is refused."""
    response = register_student(client, email='notpdf@test.com',
                                document_name='citizenship.jpg')
    assert b'Please upload a valid document' in response.data

    from models import User
    assert User.query.filter_by(email='notpdf@test.com').first() is None
```

## III.3 `tests/test_05_access_control.py` — Role Separation and Ownership

```python
def test_tc14_each_role_reaches_only_its_own_pages(client):
    """TC-14: Each role can only reach its own pages."""
    register_student(client, email='s@test.com')
    register_company(client, email='c@test.com')
    approve_all(client)

    # a student must not reach the administrator's user list
    login(client, 's@test.com')
    response = client.get('/users', follow_redirects=True)
    assert b'Manage Users' not in response.data
    client.get('/logout')

    # a company must not reach the student's applications page
    login(client, 'c@test.com')
    response = client.get('/my_applications', follow_redirects=True)
    assert b'My Applications' not in response.data


def test_tc14_company_manages_only_its_own_internships(client):
    """TC-14 (ownership): a company can only manage its own internships."""
    register_company(client, email='one@test.com', name='Company One')
    register_company(client, email='two@test.com', name='Company Two')
    approve_all(client)

    # company one posts an internship
    login(client, 'one@test.com')
    client.post('/internships/add', data={
        'title': 'Backend Intern', 'description': 'Flask work',
        'required_skills': 'Python', 'duration_weeks': '12',
        'stipend': 'Rs. 10000', 'vacancies': '2'}, follow_redirects=True)
    from models import Internship
    internship_id = Internship.query.first().id
    client.get('/logout')

    # company two must not be able to open its applicant list
    login(client, 'two@test.com')
    response = client.get(f'/applicants/{internship_id}', follow_redirects=True)
    assert b'Internship not found' in response.data
```

## III.4 `tests/test_07_admin.py` — Cascade Deletion

```python
def test_tc15_deleting_a_company_cascades(client):
    """TC-15: Deleting a company removes its internships and applications."""
    register_student(client, email='s@test.com')
    register_company(client, email='c@test.com')
    approve_all(client)

    login(client, 'c@test.com')
    client.post('/internships/add', data={
        'title': 'Data Intern', 'description': 'Reporting',
        'required_skills': 'SQL', 'duration_weeks': '8',
        'stipend': 'Rs. 8000', 'vacancies': '1'}, follow_redirects=True)
    client.get('/logout')

    from models import User, Internship, Application
    internship = Internship.query.first()

    login(client, 's@test.com')
    client.post(f'/apply/{internship.id}',
                data={'cover_letter': 'I am interested.'}, follow_redirects=True)
    client.get('/logout')

    assert Internship.query.count() == 1
    assert Application.query.count() == 1

    # the administrator deletes the company user
    login(client, 'admin@portal.com', 'admin123')
    company_user = User.query.filter_by(email='c@test.com').first()
    client.post(f'/users/delete/{company_user.id}', follow_redirects=True)

    # the internship and the application went with it
    assert Internship.query.count() == 0
    assert Application.query.count() == 0
```

## III.5 `tests/test_11_verification.py` — The Verification Gate

```python
def test_tc26_new_accounts_start_pending(client):
    """TC-26: Every new account waits for admin approval; the admin is approved."""
    register_student(client, email='new@test.com')

    from models import User
    student = User.query.filter_by(email='new@test.com').first()
    assert student.verification_status == 'pending'
    assert student.is_verified is False

    admin = User.query.filter_by(email='admin@portal.com').first()
    assert admin.verification_status == 'verified'


def test_tc26_pending_accounts_cannot_act(client):
    """TC-26: A pending company cannot post, and a pending student cannot apply."""
    register_company(client, email='c@test.com')

    login(client, 'c@test.com')
    response = client.post('/internships/add', data={
        'title': 'Should Not Exist', 'description': 'x',
        'required_skills': 'x', 'duration_weeks': '4',
        'stipend': '0', 'vacancies': '1'}, follow_redirects=True)
    assert b'waiting for admin approval' in response.data

    from models import Internship
    assert Internship.query.count() == 0


def test_tc26_rejected_account_is_told_why(client):
    """TC-26: A rejected account is told why, and still cannot act."""
    register_student(client, email='r@test.com')

    from models import User
    student = User.query.filter_by(email='r@test.com').first()

    login(client, 'admin@portal.com', 'admin123')
    client.post(f'/reject/{student.id}',
                data={'remarks': 'The document was not readable'},
                follow_redirects=True)
    client.get('/logout')

    from models import User as U
    student = U.query.filter_by(email='r@test.com').first()
    assert student.verification_status == 'rejected'
    assert student.verification_remarks == 'The document was not readable'

    # the reason is shown to the user
    login(client, 'r@test.com')
    response = client.get('/dashboard', follow_redirects=True)
    assert b'The document was not readable' in response.data
```

## III.6 Running the Tests

```
# every test
python -m pytest tests/ -v

# one file
python -m pytest tests/test_03_application.py -v

# one case
python -m pytest tests/test_01_authentication.py::test_tc01_student_registration -v
```

On Windows, `run_tests.bat` runs the full suite.

---

*End of report.*
