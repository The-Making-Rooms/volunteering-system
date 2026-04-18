# Database Entity Relationship Diagram

This document contains a comprehensive Entity Relationship Diagram (ERD) for the Volunteering System database, generated from the Django models.

## Mermaid ERD

```mermaid
erDiagram
    %% Core User and Authentication
    User {
        int id PK
        string username
        string email
        string first_name
        string last_name
        string password
    }

    %% Volunteer Module
    Volunteer {
        int id PK
        int user_id FK "OneToOne"
        string preferred_name
        image avatar
        date date_of_birth
        string phone_number
        text bio
        file CV
    }

    VolunteerAddress {
        int id PK
        int volunteer_id FK
        string first_line
        string second_line
        string postcode
        string city
    }

    EmergencyContacts {
        int id PK
        int volunteer_id FK
        string name
        string relation
        string phone_number
        string email
    }

    VolunteerConditions {
        int id PK
        int volunteer_id FK
        text disclosures
    }

    VolunteerContactPreferences {
        int id PK
        int volunteer_id FK
        boolean email
        boolean whatsapp
        boolean phone
    }

    VolunteerInterest {
        int id PK
        int volunteer_id FK
        int tag_id FK
    }

    SupplementaryInfo {
        int id PK
        string title
        string description
        int organisation_id FK
    }

    VolunteerSupplementaryInfo {
        int id PK
        int volunteer_id FK
        int info_id FK
        date last_updated
        string data
    }

    SupplementaryInfoGrantee {
        int id PK
        int org_id FK
        int info_id FK
        int volunteer_id FK
    }

    MentorRecord {
        int id PK
        int volunteer_id FK "OneToOne"
        int organisation_id FK
    }

    MentorSession {
        int id PK
        int mentor_record_id FK
        int mentor_user_id FK
        date date
        duration time
        text session_notes
    }

    MentorNotes {
        int id PK
        int MentorRecord_id FK
        int created_by_id FK
        text note
        datetime created_at
        datetime last_updated
    }

    %% Organisation Module
    Organisation {
        int id PK
        string name
        image logo
        text description
        boolean featured
    }

    OrganisationSection {
        int id PK
        int organisation_id FK
        string title
        string content
        int order
    }

    Location {
        int id PK
        int organisation_id FK
        string name
        string address
        string place_id
        float longitude
        float latitude
    }

    LinkType {
        int id PK
        file icon
        string name
    }

    Link {
        int id PK
        int link_type_id FK
        int organisation_id FK
        string url
        int clicks
    }

    Image_Org {
        int id PK
        int organisation_id FK
        image image
        image thumbnail_image
    }

    Video_Org {
        int id PK
        int organisation_id FK
        file video
        image video_thumbnail
    }

    Badge {
        int id PK
        int organisation_id FK
        string name
        text description
        image image
    }

    BadgeOpporunity {
        int id PK
        int opportunity_id FK
        int badge_id FK
    }

    VolunteerBadge {
        int id PK
        int badge_id FK
        int volunteer_id FK
        datetime date_awarded
    }

    thematicCategory {
        int id PK
        string hex_colour
        string name
        image image
    }

    organisationnThematicLink {
        int id PK
        int organisation_id FK
        int theme_id FK
    }

    OrganisationInterest {
        int id PK
        int volunteer_id FK
        int organisation_id FK
        datetime date_interest
    }

    OrganisationView {
        int id PK
        int organisation_id FK
        datetime time
    }

    %% Opportunities Module
    Opportunity {
        int id PK
        int organisation_id FK
        int form_id FK
        string name
        string description
        recurrence recurrences
        time start_time
        time end_time
        boolean active
        boolean featured
        datetime date_created
        boolean show_times_on_sign_up
        int week_start
        string rota_config
    }

    OpportunitySection {
        int id PK
        int opportunity_id FK
        string title
        string content
        int order
    }

    OpportunityView {
        int id PK
        int opportunity_id FK
        datetime time
    }

    Icon {
        int id PK
        image icon
        string name
        string tags
        boolean invert
    }

    Benefit {
        int id PK
        int icon_id FK
        int organisation_id FK
        int opportunity_id FK
        string description
    }

    OpportunityBenefit {
        int id PK
        int opportunity_id FK
        int benefit_id FK
    }

    Location_Opp {
        int id PK
        int opportunity_id FK
        string name
        string address
        string place_id
        float longitude
        float latitude
    }

    RegistrationStatus {
        int id PK
        string status
    }

    Registration {
        int id PK
        int volunteer_id FK
        int opportunity_id FK
        datetime date_created
    }

    VolunteerRegistrationStatus {
        int id PK
        int registration_id FK
        int registration_status_id FK
        datetime date
    }

    RegistrationAbsence {
        int id PK
        int registration_id FK
        date date
    }

    Image_Opp {
        int id PK
        int opportunity_id FK
        image image
        image thumbnail_image
    }

    Video_Opp {
        int id PK
        int opportunity_id FK
        file video
        image video_thumbnail
    }

    Tag {
        int id PK
        string tag
        string hex_colour
        string hex_colour_to
    }

    LinkedTags {
        int id PK
        int opportunity_id FK
        int tag_id FK
    }

    SupplimentaryInfoRequirement {
        int id PK
        int opportunity_id FK
        int info_id FK
    }

    %% Rota Module
    Schedule {
        int id PK
        int opportunity_id FK
        string name
        date start_date
        date end_date
        time start_time
        time end_time
        binary recurrence_rule
    }

    Role {
        int id PK
        int opportunity_id FK
        string name
        text description
        text volunteer_description
        int required_volunteers
        int week_start
    }

    Section {
        int id PK
        int role_id FK
        string name
        text description
        int required_volunteers
    }

    VolunteerScheduleAvailability {
        int id PK
        int registration_id FK
        int schedule_id FK
    }

    OneOffDate {
        int id PK
        int opportunity_id FK
        int role_id FK
        date date
        time start_time
        time end_time
    }

    VolunteerOneOffDateAvailability {
        int id PK
        int registration_id FK
        int one_off_date_id FK
    }

    VolunteerRoleIntrest {
        int id PK
        int registration_id FK
        int role_id FK
    }

    Occurrence {
        int id PK
        int schedule_id FK "OneToOne"
        int one_off_date_id FK "OneToOne"
        date date
        time start_time
        time end_time
    }

    VolunteerShift {
        int id PK
        int registration_id FK
        int occurrence_id FK
        int role_id FK
        int section_id FK
        boolean confirmed
        time check_in_time
        time check_out_time
        string rsvp_response
        string rsvp_reason
    }

    Supervisor {
        int id PK
        int user_id FK
        int organisation_id FK
        string access_level
    }

    Supervisor_Opportunities {
        int supervisor_id FK
        int opportunity_id FK
    }

    Supervisor_Roles {
        int supervisor_id FK
        int role_id FK
    }

    Supervisor_Shifts {
        int supervisor_id FK
        int occurrence_id FK
    }

    %% Forms Module
    Form {
        int id PK
        int organisation_id FK
        string name
        string description
        boolean allow_multiple
        boolean required_on_signup
        boolean mentor_start_form
        boolean mentor_end_form
        boolean sign_up_form
        boolean filled_by_organisation
        boolean visible_to_all
    }

    Question {
        int id PK
        int form_id FK
        int index
        string question
        string question_type
        boolean required
        boolean allow_multiple
        boolean enabled
    }

    Options {
        int id PK
        int question_id FK
        string option
    }

    Response {
        int id PK
        int user_id FK
        int form_id FK
        datetime response_date
    }

    Answer {
        int id PK
        int question_id FK
        int response_id FK
        string answer
    }

    FormResponseRequirement {
        int id PK
        int form_id FK
        int user_id FK
        boolean completed
        datetime assigned
    }

    OrganisationFormResponseRequirement {
        int id PK
        int form_id FK
        int organisation_id FK
        boolean completed
        datetime assigned
    }

    SuperForm {
        uuid id PK
        string name
        text description
        image photo
        text submitted_message
        string background_colour
        string card_background_colour
        string card_text_colour
        boolean show_form_titles
        boolean show_form_descriptions
        boolean active
        int opportunity_to_register_id FK
    }

    SuperForm_Forms {
        int superform_id FK
        int form_id FK
    }

    SuperFormRegistration {
        uuid id PK
        int user_id FK
        int superform_id FK
        datetime submitted
    }

    %% Communications Module
    Chat {
        int id PK
        int organisation_id FK
        boolean broadcast
        boolean chip_in_admins_chat
    }

    Chat_Participants {
        int chat_id FK
        int user_id FK
    }

    Message {
        int id PK
        int chat_id FK
        int sender_id FK
        text content
        datetime timestamp
        boolean automated
    }

    MessageSeen {
        int id PK
        int message_id FK
        int user_id FK
        datetime time
    }

    AutomatedMessage {
        int id PK
        int organisation_id FK "OneToOne"
        text content
    }

    %% Org Admin Module
    OrganisationAdmin {
        int id PK
        int user_id FK
        int organisation_id FK
    }

    NotificationPreference {
        int id PK
        int user_id FK "OneToOne"
        boolean email_on_message
        boolean email_on_registration
    }

    EmailDraft {
        int id PK
        int opportunity_id FK
        int organisation_id FK
        int sent_by_id FK
        string subject
        text email_quill
        text email_html
        string send_confirmation_id
        string email_target_recipients
        boolean sent
        datetime sent_date
        datetime created_date
        datetime last_modified
    }

    EmailDraft_Recipients {
        int emaildraft_id FK
        int user_id FK
    }

    %% Relationships - User & Volunteer
    User ||--o| Volunteer : "has"
    Volunteer ||--o{ VolunteerAddress : "has"
    Volunteer ||--o{ EmergencyContacts : "has"
    Volunteer ||--o| VolunteerConditions : "has"
    Volunteer ||--o| VolunteerContactPreferences : "has"
    Volunteer ||--o{ VolunteerInterest : "interested in"
    Volunteer ||--o{ VolunteerSupplementaryInfo : "has"
    Volunteer ||--o{ SupplementaryInfoGrantee : "grants access"
    Volunteer ||--o| MentorRecord : "has"
    Volunteer ||--o{ VolunteerBadge : "earned"
    Volunteer ||--o{ OrganisationInterest : "interested in"
    Volunteer ||--o{ Registration : "registers for"

    %% Organisation Relationships
    Organisation ||--o{ OrganisationSection : "has"
    Organisation ||--o{ Location : "has"
    Organisation ||--o{ Link : "has"
    Organisation ||--o{ Image_Org : "has"
    Organisation ||--o{ Video_Org : "has"
    Organisation ||--o{ Badge : "offers"
    Organisation ||--o{ organisationnThematicLink : "categorized by"
    Organisation ||--o{ OrganisationInterest : "receives interest"
    Organisation ||--o{ OrganisationView : "viewed"
    Organisation ||--o{ Opportunity : "provides"
    Organisation ||--o{ OrganisationAdmin : "administered by"
    Organisation ||--o{ MentorRecord : "mentors"
    Organisation ||--o{ SupplementaryInfo : "defines"
    Organisation ||--o{ SupplementaryInfoGrantee : "receives access"
    Organisation ||--o{ Form : "owns"
    Organisation ||--o{ Benefit : "offers"
    Organisation ||--o{ Chat : "communicates"
    Organisation ||--o| AutomatedMessage : "has"
    Organisation ||--o{ OrganisationFormResponseRequirement : "requires"
    Organisation ||--o{ Supervisor : "supervises"
    Organisation ||--o{ EmailDraft : "sends"

    %% Opportunity Relationships
    Opportunity ||--o{ OpportunitySection : "has"
    Opportunity ||--o{ OpportunityView : "viewed"
    Opportunity ||--o{ Benefit : "offers"
    Opportunity ||--o{ OpportunityBenefit : "linked to"
    Opportunity ||--o{ Location_Opp : "at"
    Opportunity ||--o{ Registration : "receives"
    Opportunity ||--o{ Image_Opp : "has"
    Opportunity ||--o{ Video_Opp : "has"
    Opportunity ||--o{ LinkedTags : "tagged with"
    Opportunity ||--o{ SupplimentaryInfoRequirement : "requires"
    Opportunity ||--o{ BadgeOpporunity : "awards"
    Opportunity ||--o{ Schedule : "scheduled"
    Opportunity ||--o{ Role : "has"
    Opportunity ||--o{ OneOffDate : "has"
    Opportunity ||--o{ Supervisor_Opportunities : "supervised by"
    Opportunity ||--o| SuperForm : "registered via"
    Opportunity ||--o{ EmailDraft : "emails"

    %% Registration & Status
    Registration ||--o{ VolunteerRegistrationStatus : "has status"
    Registration ||--o{ RegistrationAbsence : "has absences"
    Registration ||--o{ VolunteerScheduleAvailability : "available for"
    Registration ||--o{ VolunteerOneOffDateAvailability : "available for"
    Registration ||--o{ VolunteerRoleIntrest : "interested in"
    Registration ||--o{ VolunteerShift : "assigned to"

    %% Rota Relationships
    Schedule ||--o| Occurrence : "generates"
    OneOffDate ||--o| Occurrence : "generates"
    OneOffDate ||--o{ VolunteerOneOffDateAvailability : "available to"
    Role ||--o{ Section : "divided into"
    Role ||--o{ VolunteerRoleIntrest : "interests"
    Role ||--o{ VolunteerShift : "assigned"
    Role ||--o{ OneOffDate : "specific to"
    Role ||--o{ Supervisor_Roles : "supervised by"
    Section ||--o{ VolunteerShift : "assigned"
    Occurrence ||--o{ VolunteerShift : "scheduled"
    Occurrence ||--o{ Supervisor_Shifts : "supervised by"
    Schedule ||--o{ VolunteerScheduleAvailability : "available to"

    %% Forms Relationships
    Form ||--o{ Question : "contains"
    Form ||--o{ Response : "receives"
    Form ||--o{ FormResponseRequirement : "required from"
    Form ||--o{ OrganisationFormResponseRequirement : "required from"
    Form ||--o{ SuperForm_Forms : "included in"
    Form ||--o{ Opportunity : "used for"
    Question ||--o{ Options : "has"
    Question ||--o{ Answer : "answered by"
    Response ||--o{ Answer : "contains"

    %% SuperForm Relationships
    SuperForm ||--o{ SuperFormRegistration : "registered"

    %% Communications Relationships
    Chat ||--o{ Message : "contains"
    Chat ||--o{ Chat_Participants : "includes"
    Message ||--o{ MessageSeen : "seen by"

    %% Linking Tables
    LinkType ||--o{ Link : "categorizes"
    thematicCategory ||--o{ organisationnThematicLink : "categorizes"
    Tag ||--o{ LinkedTags : "tags"
    Tag ||--o{ VolunteerInterest : "interests"
    Icon ||--o{ Benefit : "represents"
    Benefit ||--o{ OpportunityBenefit : "linked to"
    Badge ||--o{ BadgeOpporunity : "awarded for"
    Badge ||--o{ VolunteerBadge : "awarded to"
    SupplementaryInfo ||--o{ VolunteerSupplementaryInfo : "filled by"
    SupplementaryInfo ||--o{ SupplimentaryInfoRequirement : "required"
    RegistrationStatus ||--o{ VolunteerRegistrationStatus : "defines"

    %% Admin & User Relationships
    User ||--o{ OrganisationAdmin : "administers"
    User ||--o| NotificationPreference : "has"
    User ||--o{ Response : "submits"
    User ||--o{ FormResponseRequirement : "required to complete"
    User ||--o{ SuperFormRegistration : "submits"
    User ||--o{ Chat_Participants : "participates in"
    User ||--o{ Message : "sends"
    User ||--o{ MessageSeen : "sees"
    User ||--o{ MentorSession : "mentors"
    User ||--o{ MentorNotes : "creates"
    User ||--o{ Supervisor : "supervises"
    User ||--o{ EmailDraft : "sends"
    User ||--o{ EmailDraft_Recipients : "receives"

    %% Supervisor Relationships
    Supervisor ||--o{ Supervisor_Opportunities : "manages"
    Supervisor ||--o{ Supervisor_Roles : "manages"
    Supervisor ||--o{ Supervisor_Shifts : "manages"

    %% MentorRecord Relationships
    MentorRecord ||--o{ MentorSession : "tracks"
    MentorRecord ||--o{ MentorNotes : "has"
```

## Model Summary

### Core Modules

1. **User & Volunteer Module** (volunteer/models.py)
   - Volunteer, VolunteerAddress, EmergencyContacts, VolunteerConditions
   - VolunteerContactPreferences, VolunteerInterest
   - SupplementaryInfo, VolunteerSupplementaryInfo, SupplementaryInfoGrantee
   - MentorRecord, MentorSession, MentorNotes

2. **Organisation Module** (organisations/models.py)
   - Organisation, OrganisationSection, Location
   - LinkType, Link, Image, Video
   - Badge, BadgeOpporunity, VolunteerBadge
   - thematicCategory, organisationnThematicLink
   - OrganisationInterest, OrganisationView

3. **Opportunities Module** (opportunities/models.py)
   - Opportunity, OpportunitySection, OpportunityView
   - Icon, Benefit, OpportunityBenefit
   - Location (opportunity-specific)
   - Registration, RegistrationStatus, VolunteerRegistrationStatus, RegistrationAbsence
   - Image, Video (opportunity-specific)
   - Tag, LinkedTags
   - SupplimentaryInfoRequirement

4. **Rota/Scheduling Module** (rota/models.py)
   - Schedule, Role, Section
   - OneOffDate, Occurrence
   - VolunteerScheduleAvailability, VolunteerOneOffDateAvailability
   - VolunteerRoleIntrest, VolunteerShift
   - Supervisor (with ManyToMany for opportunities, roles, shifts)

5. **Forms Module** (forms/models.py)
   - Form, Question, Options
   - Response, Answer
   - FormResponseRequirement, OrganisationFormResponseRequirement
   - SuperForm, SuperFormRegistration

6. **Communications Module** (communications/models.py)
   - Chat, Message, MessageSeen
   - AutomatedMessage

7. **Org Admin Module** (org_admin/models.py)
   - OrganisationAdmin, NotificationPreference
   - EmailDraft

### Key Relationships

- **One-to-One**: User ↔ Volunteer, Volunteer ↔ MentorRecord, Organisation ↔ AutomatedMessage
- **One-to-Many**: Organisation → Opportunities, Opportunity → Registrations, Organisation → Forms
- **Many-to-Many**: Chat ↔ Users (participants), SuperForm ↔ Forms, Supervisor ↔ Opportunities/Roles/Shifts

### Total Models: 74

This ERD represents the complete database schema for the Volunteering System as of 2026-02-07.
