# Button and Icon Reference

Every button in the system, the page it appears on, what it does, and the
Bootstrap Icon used. Icons come from **Bootstrap Icons**, served from
`static/bootstrap-icons.css` with the font files in `static/fonts/`, so the
system works without an internet connection.

## Public pages

| Page | Button | Icon | Action |
|------|--------|------|--------|
| Landing | Get Started | `bi-rocket-takeoff` | Go to registration |
| Landing | Login | `bi-box-arrow-in-right` | Go to login |
| Login | Login | `bi-box-arrow-in-right` | Sign in |
| Registration choice | Register as Student | `bi-mortarboard` | Student form |
| Registration choice | Register as Company | `bi-building` | Company form |
| Registration choice | Register as Supervisor | `bi-person-badge` | Supervisor form |
| Student form | Register | `bi-person-plus` | Create student account |
| Company form | Register | `bi-person-plus` | Create company account |
| Supervisor form | Register | `bi-person-plus` | Create supervisor account |

## Student

| Page | Button | Icon | Action |
|------|--------|------|--------|
| Internships | Search | `bi-search` | Filter by keyword and skill |
| Internships | Clear | `bi-x-circle` | Reset the search |
| Internships | Apply | `bi-send` | Submit application with cover letter |
| My Applications | Weekly Logs | `bi-journal-text` | Open the log book |
| My Applications | Withdraw | `bi-x-circle` | Cancel a pending application |
| Weekly Log Book | Submit Log | `bi-send` | Save this week's entry |
| Weekly Log Book | Back to my applications | `bi-arrow-left` | Return |

## Company

| Page | Button | Icon | Action |
|------|--------|------|--------|
| Internships | View applicants | `bi-people` | See who applied |
| Internships | Edit | `bi-pencil-square` | Change the posting |
| Internships | Delete | `bi-trash` | Remove the posting |
| Post Internship | Post | `bi-plus-circle` | Publish a new internship |
| Edit Internship | Save Changes | `bi-save` | Store the changes |
| Applicants | Update Status | `bi-arrow-repeat` | Select or reject |
| Applicants | Export CSV | `bi-file-earmark-arrow-down` | Download applicant list |
| Applicants | Back to internships | `bi-arrow-left` | Return |

## Supervisor

| Page | Button | Icon | Action |
|------|--------|------|--------|
| My Students | View logs | `bi-journal-text` | Open a student's log book |
| Log Review | Save Feedback | `bi-check-circle` | Record feedback and marks |
| Log Review | Back to my students | `bi-arrow-left` | Return |

## Administrator

| Page | Button | Icon | Action |
|------|--------|------|--------|
| Users | Search | `bi-search` | Find users by name or email |
| Users | Clear | `bi-x-circle` | Reset the search |
| Users | Export CSV | `bi-file-earmark-arrow-down` | Download the user list |
| Users | Delete | `bi-trash` | Remove a user and their data |
| Colleges | Add College | `bi-plus-circle` | Register a new college |
| Colleges | Remove | `bi-trash` | Remove a college |

## Navigation bar (all roles)

| Item | Icon |
|------|------|
| Dashboard | `bi-speedometer2` |
| Internships | `bi-briefcase` |
| My Applications | `bi-file-earmark-text` |
| Post Internship | `bi-plus-square` |
| My Students | `bi-people` |
| Users | `bi-person-gear` |
| Colleges | `bi-building` |
| Audit Log | `bi-clock-history` |
| Notifications | `bi-bell` (with unread count badge) |
| Login | `bi-box-arrow-in-right` |
| Register | `bi-person-plus` |
| Logout | `bi-box-arrow-right` |

## Icon choices explained

- **Destructive actions** (Delete, Remove, Withdraw) use `bi-trash` or
  `bi-x-circle` with red outline buttons, so they are visually distinct from
  safe actions.
- **Creating** something uses a plus icon; **saving** an existing record uses
  `bi-save` or `bi-check-circle`.
- **Sending** something to another person (applying, submitting a log) uses
  `bi-send`.
- **Navigation back** always uses `bi-arrow-left`.
- The same action always uses the same icon across pages, so users learn the
  interface once.

## Adding the project logo

Save the logo as **`static/logo.png`**. It then appears automatically in the
navigation bar, on the landing page above the heading, and as the browser tab
icon. If the file is not present the system falls back to the text title, so
nothing breaks.
