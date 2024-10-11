from abstra.tables import select, insert, update_by_id, delete_by_id, select_one
import re


def extract_linkedin_handle(txt: str) -> str:
    match = re.search(r"(https://)?(www.)?(linkedin.com/in/|linkedin.com/company/|linkedin.com/school/)[^/]+", txt)
    if match:
        return match.group().split("/")[-1]
    # raise exception if not linkedin url
    match = re.search(r"(https://)?(www.)?([^/]+.)?([^/]+.)/.*", txt)
    if match:
        raise ValueError("Invalid linkedin url")
    return txt


class Company:

    table_name = 'companies'

    def __init__(self, row) -> None:

        self.id = row['id']
        self.name = row['name']
        self.site = row['site']
        self.linkedin_handle = row['linkedin_handle']
        self.owner = row['owner']
        self.airtable_id = row['airtable_id']

    @staticmethod
    def insert(name=None, site=None, linkedin_handle=None, owner=None, airtable_id=None):

        data = {
            'name': name.title(),
            'site': site,
            'linkedin_handle': linkedin_handle,
            'owner': owner,
            'airtable_id': airtable_id
        }

        return Company(insert(Company.table_name, data))

    @staticmethod
    def select_by(id=None, linkedin_handle=None, airtable_id=None):

        if all([id is None, linkedin_handle is None, airtable_id is None]):
            rows = select(Company.table_name)
            return [Company(row) for row in rows]

        where_clause = {}

        if id is not None:
            where_clause['id'] = id
        if linkedin_handle is not None:
            where_clause['linkedin_handle'] = linkedin_handle
        if airtable_id is not None:
            where_clause['airtable_id'] = airtable_id

        rows = select(Company.table_name, where=where_clause)

        return [Company(row) for row in rows]
    

class Lead:

    table_name = 'leads'

    def __init__(self, row) -> None:

        self.id = row['id']
        self.name = row['name']
        self.email = row['email']
        self.company_id = row['company_id']
        self.linkedin_handle = row['linkedin_handle']
        self.phone_number = row['phone_number']
        self.airtable_id = row['airtable_id']

    @staticmethod
    def insert(name=None, email=None, company_id=None, linkedin_handle=None, phone_number=None, airtable_id=None):

        data = {
            'name': name.title(),
            'email': email.lower(),
            'company_id': company_id,
            'linkedin_handle': linkedin_handle,
            'phone_number': phone_number,
            'airtable_id': airtable_id
        }

        return Lead(insert(Lead.table_name, data))

    @staticmethod
    def select_by(id=None, company_id=None, email=None, linkedin_handle=None):

        if all([id is None, company_id is None, email is None, linkedin_handle is None]):

            rows = select(Lead.table_name)
            return [Lead(row) for row in rows]

        where_clause = {}

        if id is not None:
            where_clause['id'] = id

        if company_id is not None:
            where_clause['company_id'] = company_id

        if email is not None:
            where_clause['email'] = email

        if linkedin_handle is not None:
            where_clause['linkedin_handle'] = linkedin_handle

        rows = select(Lead.table_name, where=where_clause)
        return [Lead(row) for row in rows]
    

class Opportunity:

    table_name = 'opportunities'

    def __init__(self, row) -> None:
        
        self.id = row['id']
        self.company_id = row['company_id']
        self.use_case = row['use_case']
        self.owner_team_id = row['owner_team_id']
        self.motion = row['motion']
        self.airtable_id = row['airtable_id']

    @staticmethod
    def insert(company_id=None, use_case=None, owner_team_id=None, motion=None, airtable_id=None):

        data = {
            'company_id': company_id,
            'use_case': use_case,
            'owner_team_id': owner_team_id,
            'motion': motion,
            'airtable_id': airtable_id
        }

        return Opportunity(insert(Opportunity.table_name, data))
    
    @staticmethod
    def select_by(id=None, company_id=None):

        if all([id is None, company_id is None]):

            rows = select(Opportunity.table_name)
            return [Opportunity(row) for row in rows]

        where_clause = {}

        if id is not None:
            where_clause['id'] = id

        if company_id is not None:
            where_clause['company_id'] = company_id

        rows = select(Opportunity.table_name, where=where_clause)
        return [Opportunity(row) for row in rows]
    

class OpportunityExpectations:
    
    table_name = 'opportunity_expectations'

    def __init__(self, row) -> None:

        self.id = row['id']
        self.opportunity_id = row['opportunity_id']
        self.company_id = row['company_id']
        self.min_mrr = row['min_mrr']
        self.max_mrr = row['max_mrr']

    @staticmethod
    def insert(opportunity_id=None, company_id=None, min_mrr=None, max_mrr=None):

        data = {
            'opportunity_id': opportunity_id,
            'company_id': company_id,
            'min_mrr': min_mrr,
            'max_mrr': max_mrr
        }

        return OpportunityExpectations(insert(OpportunityExpectations.table_name, data))

    
class OpportunityStatusUpdates:

    table_name = 'opportunity_status_updates'

    def __init__(self, row) -> None:
            
            self.id = row['id']
            self.company_id = row['company_id']
            self.opportunity_id = row['opportunity_id']
            self.type = row['type']
            self.lost = row['lost']
            self.lost_reason = row['lost_reason']

    @staticmethod
    def insert(company_id=None, opportunity_id=None, type=None, lost=None, lost_reason=None, lost_at=None):

        data = {
            'company_id': company_id,
            'opportunity_id': opportunity_id,
            'type': type,
            'lost': lost,
            'lost_reason': lost_reason,
            'lost_at': lost_at
        }

        return OpportunityStatusUpdates(insert(OpportunityStatusUpdates.table_name, data))
    
    @staticmethod
    def select_by(opportunity_id=None):

        if all([opportunity_id is None]):

            rows = select(OpportunityStatusUpdates.table_name)
            return [OpportunityStatusUpdates(row) for row in rows]
        
        where_clause = {}

        if opportunity_id is not None:
            where_clause['opportunity_id'] = opportunity_id

        rows = select(OpportunityStatusUpdates.table_name, where=where_clause)
        return [OpportunityStatusUpdates(row) for row in rows]
    
    @staticmethod
    def select_last_status(opportunity_id=None):

        where_clause = {}

        if opportunity_id is not None:
            where_clause['opportunity_id'] = opportunity_id

        rows = select(OpportunityStatusUpdates.table_name, where=where_clause)

        if not rows:
            return None
        
        last_status = rows[0]

        for row in rows[1:]:
            if row['created_at'] > last_status['created_at']:
                last_status = row

        return OpportunityStatusUpdates(last_status)
    

class Sourcing:
    
    table_name = 'sourcing'

    def __init__(self, row) -> None:

        self.id = row['id']
        self.lead_id = row['lead_id']
        self.channel = row['channel']

    @staticmethod
    def insert(lead_id=None, channel=None):

        data = {
            'lead_id': lead_id,
            'channel': channel
        }

        return Sourcing(insert(Sourcing.table_name, data))
    

class LeadStatusUpdates:

    table_name = 'lead_status_updates'

    def __init__(self, row) -> None:

        self.id = row['id']
        self.lead_id = row['lead_id']
        self.opportunity_id = row['opportunity_id']
        self.status = row['status']

    @staticmethod
    def insert(lead_id=None, opportunity_id=None, status=None):

        data = {
            'lead_id': lead_id,
            'opportunity_id': opportunity_id,
            'status': status
        }

        return LeadStatusUpdates(insert(LeadStatusUpdates.table_name, data))
    
    @staticmethod
    def select_last_status(lead_id=None, opportunity_id=None):

        where_clause = {}

        if lead_id is not None:
            where_clause['lead_id'] = lead_id

        if opportunity_id is not None:
            where_clause['opportunity_id'] = opportunity_id

        rows = select(LeadStatusUpdates.table_name, where=where_clause)

        if not rows:
            return None
        
        last_status = rows[0]

        for row in rows[1:]:
            if row['created_at'] > last_status['created_at']:
                last_status = row

        return LeadStatusUpdates(last_status)
    

class Touchpoint:

    table_name = 'touchpoints'

    def __init__(self, row) -> None:

        self.id = row['id']
        self.channel = row['channel']
        self.company_id = row['company_id']
        self.touchpoint_date = row['touchpoint_date']
        self.title = row['title']
        self.happened = row['happened']
        self.google_calendar_id = row['google_calendar_id']
        self.google_calendar_json = row['google_calendar_json']
        self.organizer_team_id = row['organizer_team_id']
        self.processed = row['processed']
        self.ignore = row['ignore']
        self.updated_at = row['updated_at']

    @staticmethod
    def insert(
        channel=None, 
        company_id=None, 
        touchpoint_date=None, 
        title=None, 
        happened=None, 
        google_calendar_id=None,
        google_calendar_json=None,
        organizer_team_id=None,
        processed=None
    ):

        data = {
            'channel': channel,
            'company_id': company_id,
            'touchpoint_date': touchpoint_date,
            'title': title,
            'happened': happened,
            'google_calendar_id': google_calendar_id,
            'google_calendar_json': google_calendar_json,
            'organizer_team_id': organizer_team_id,
            'processed': processed
        }

        return Touchpoint(insert(Touchpoint.table_name, data))
    
    @staticmethod
    def select_by(id=None, organizer_team_id=None, processed=None, ignore=None):

        if all([id is None, organizer_team_id is None, processed is None, ignore is None]):

            rows = select(Touchpoint.table_name)
            return [Touchpoint(row) for row in rows]
        
        where_clause = {}

        if id is not None:
            where_clause['id'] = id
        if organizer_team_id is not None:
            where_clause['organizer_team_id'] = organizer_team_id
        if processed is not None:
            where_clause['processed'] = processed
        if ignore is not None:
            where_clause['ignore'] = ignore

        rows = select(Touchpoint.table_name, where=where_clause)
        return [Touchpoint(row) for row in rows]
    
    @staticmethod
    def update_by_id(
        id,
        company_id=None, 
        title=None, 
        happened=None, 
        processed=None,
        channel=None,
        ignore=None,
        updated_at=None
    ):
        
        data = {}

        if title:
            data['title'] = title
        if happened:
            data['happened'] = happened
        if processed:
            data['processed'] = processed
        if company_id:
            data['company_id'] = company_id
        if channel:
            data['channel'] = channel
        if ignore:
            data['ignore'] = ignore
        if updated_at:
            data['updated_at'] = updated_at

        update_by_id(Touchpoint.table_name, id=id, values=data)
    

class TouchpointLeads:

    table_name = 'touchpoints_leads'

    def __init__(self, row) -> None:

        self.id = row['id']
        self.touchpoint_id = row['touchpoint_id']
        self.lead_id = row['lead_id']

    @staticmethod
    def insert(touchpoint_id=None, lead_id=None):

        data = {
            'touchpoint_id': touchpoint_id,
            'lead_id': lead_id
        }

        return TouchpointLeads(insert(TouchpointLeads.table_name, data))


class OpportunityLeads:

    table_name = 'opportunity_leads'

    def __init__(self, row) -> None:

        self.id = row['id']
        self.opportunity_id = row['opportunity_id']
        self.lead_id = row['lead_id']

    @staticmethod
    def select_by(opportunity_id=None, lead_id=None):

        if all([opportunity_id is None, lead_id is None]):

            rows = select(OpportunityLeads.table_name)
            return [OpportunityLeads(row) for row in rows]

        where_clause = {}

        if opportunity_id is not None:
            where_clause['opportunity_id'] = opportunity_id

        if lead_id is not None:
            where_clause['lead_id'] = lead_id

        rows = select(OpportunityLeads.table_name, where=where_clause)
        return [OpportunityLeads(row) for row in rows]

    @staticmethod
    def insert(opportunity_id=None, lead_id=None):

        data = {
            'opportunity_id': opportunity_id,
            'lead_id': lead_id
        }

        return OpportunityLeads(insert(OpportunityLeads.table_name, data))
    

class FormOptions:

    table_name = 'touchpoint_form_options'

    def __init__(self, rows) -> None:
        
        self.channel_options = []
        self.opportunity_status_options = []
        self.lost_options = []
        self.lead_status_options = []
        self.lead_sourcing_options = []
        self.opportunity_motion = []

        for row in rows:
            if row['field'] == 'channel_options':
                self.channel_options = row['data']['options']
            elif row['field'] == 'opportunity_status_options':
                self.opportunity_status_options = row['data']['options']
            elif row['field'] == 'lost_options':
                self.lost_options = row['data']['options']

            elif row['field'] == 'lead_status_options':
                for i in range(len(row['data']['options'])):
                    option = row['data']['options'][i]
                    
                    if i < len(row['data']['description']):
                        description = f" - {row['data']['description'][i]}"
                    else:
                        description = ''

                    self.lead_status_options.append({
                        'value': option,
                        'label': f"{option}{description}"
                    })

            elif row['field'] == 'lead_sourcing_options':
                self.lead_sourcing_options = row['data']['options']
            elif row['field'] == 'opportunity_motion':
                self.opportunity_motion = row['data']['options']
            else:
                pass


    @staticmethod
    def retrieve():
        rows = select(FormOptions.table_name)
        return FormOptions(rows)
    

class LinkedinCompanySnapshot:

    table_name = 'linkedin_company_snapshots'

    def __init__(self, row) -> None:

        self.id = row['id']
        self.headcount = row['headcount']
        self.industry = row['industry']
        self.raw_summary = row['raw_summary']
        self.processed = row['processed']
        self.company_id = row['company_id']

    def update(self):
            
        data = {
            'headcount': self.headcount,
            'industry': self.industry,
            'raw_summary': self.raw_summary,
            'processed': self.processed,
            'company_id': self.company_id
        }

        update_by_id(LinkedinCompanySnapshot.table_name, id=self.id, values=data)
                         
    @staticmethod
    def insert(headcount=None, industry=None, raw_summary=None, company_id=None):

        data = {
            'headcount': headcount,
            'industry': industry,
            'raw_summary': raw_summary,
            'company_id': company_id
        }

        return LinkedinCompanySnapshot(insert(LinkedinCompanySnapshot.table_name, data))
    
    @staticmethod
    def select_by(id=None, processed=None, company_id=None):

        if all([id is None, processed is None, company_id is None]):

            rows = select(LinkedinCompanySnapshot.table_name)
            return [LinkedinCompanySnapshot(row) for row in rows]
        
        where_clause = {}

        if id is not None:
            where_clause['id'] = id
        if processed is not None:
            where_clause['processed'] = processed
        if company_id is not None:
            where_clause['company_id'] = company_id

        rows = select(LinkedinCompanySnapshot.table_name, where=where_clause)
        return [LinkedinCompanySnapshot(row) for row in rows]
    

class LinkedinPeopleSnapshot:

    table_name = 'linkedin_people_snapshots'

    def __init__(self, row) -> None:

        self.id = row['id']
        self.job_title = row['job_title']
        self.raw_summary = row['raw_summary']
        self.processed = row['processed']
        self.lead_id = row['lead_id']

    def update(self):

        data = {
            'job_title': self.job_title,
            'raw_summary': self.raw_summary,
            'processed': self.processed,
            'lead_id': self.lead_id
        }

        update_by_id(LinkedinPeopleSnapshot.table_name, id=self.id, values=data)

    @staticmethod
    def insert(job_title=None, raw_summary=None, lead_id=None):

        data = {
            'job_title': job_title,
            'raw_summary': raw_summary,
            'lead_id': lead_id
        }

        return LinkedinPeopleSnapshot(insert(LinkedinPeopleSnapshot.table_name, data))
    
    @staticmethod
    def select_by(id=None, processed=None, lead_id=None):

        if all([id is None, processed is None, lead_id is None]):

            rows = select(LinkedinPeopleSnapshot.table_name)
            return [LinkedinPeopleSnapshot(row) for row in rows]
        
        where_clause = {}

        if id is not None:
            where_clause['id'] = id
        if processed is not None:
            where_clause['processed'] = processed
        if lead_id is not None:
            where_clause['lead_id'] = lead_id

        rows = select(LinkedinPeopleSnapshot.table_name, where=where_clause)
        return [LinkedinPeopleSnapshot(row) for row in rows]


class TLDV_Meeting:
     
    table_name = 'tldv_meetings'

    def __init__(self, row) -> None:
        self.id = row['id']
        self.meeting_id = row['meeting_id']
        self.summary = row['summary']
        self.meeting_date = row['meeting_date']
        self.meeting_name = row['meeting_name']

    @staticmethod
    def insert(meeting_id, summary, meeting_date, meeting_name):

        data = {
            'meeting_id': meeting_id, 
            'summary': summary,
            'meeting_date': meeting_date,
            'meeting_name': meeting_name,
        }

        return TLDV_Meeting(insert(TLDV_Meeting.table_name, data))
    
    @staticmethod
    def select_by(meeting_id=None, summary=None, meeting_date=None, meeting_name=None):

        if all([meeting_id is None, summary is None, meeting_date is None, meeting_name is None]):

            rows = select(TLDV_Meeting.table_name)
            return [TLDV_Meeting(row) for row in rows]
        
        where_clause = {}

        if meeting_id is not None:
            where_clause['meeting_id'] = meeting_id
        if summary is not None:
            where_clause['summary'] = summary
        if meeting_date is not None:
            where_clause['meeting_date'] = meeting_date
        if meeting_name is not None:
            where_clause['meeting_name'] = meeting_name
        
        rows = select(TLDV_Meeting.table_name, where=where_clause)
        return [TLDV_Meeting(row) for row in rows]
    

class TLDV_Meeting_Leads:

    table_name = 'tldv_meeting_leads'

    def __init__(self, row) -> None:
        self.meeting_id = row['meeting_id']
        self.lead_id = row['lead_id']

    @staticmethod
    def select_by(meeting_id=None, lead_id=None):
        
        if all([meeting_id is None, lead_id is None]):

            rows_list = select(TLDV_Meeting_Leads.table_name)
            return [TLDV_Meeting_Leads(row) for row in rows_list]
        
        where_clause = {}

        if meeting_id is not None:
            where_clause['meeting_id'] = meeting_id
        
        if lead_id is not None:
            where_clause['lead_id'] = lead_id

        rows = select(TLDV_Meeting_Leads.table_name, where=where_clause)
        return [TLDV_Meeting_Leads(row) for row in rows]

    @staticmethod
    def insert(meeting_id, lead_id):
        data = {
            'meeting_id': meeting_id,
            'lead_id': lead_id,
        }

        return TLDV_Meeting_Leads(insert(TLDV_Meeting_Leads.table_name, data))

    
class Team:

    table_name = 'team'

    def __init__(self, row: dict) -> None:

        self.id = row['id']
        self.email = row['email']
        self.name = row['name']

    @staticmethod
    def select_one_by(id=None, email=None):

        if all([id is None, email is None]):

            row = select_one(Team.table_name)
            return Team(row)
        
        where_clause = {}

        if id is not None:
            where_clause['id'] = id
        if email is not None:
            where_clause['email'] = email
        
        row = select_one(Team.table_name, where=where_clause)

        return Team(row)

    @staticmethod
    def select_by(id=None, email=None):

        if all([id is None, email is None]):

            rows = select(Team.table_name)
            return [Team(row) for row in rows]
        
        where_clause = {}

        if id is not None:
            where_clause['id'] = id
        if email is not None:
            where_clause['email'] = email

        rows = select(Team.table_name, where=where_clause)
        return [Team(row) for row in rows]
