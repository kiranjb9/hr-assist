from mcp.server.fastmcp import FastMCP
from hrms import *
from utils import seed_services
from emails import EmailSender
import os
from dotenv import load_dotenv

_ = load_dotenv()

mcp = FastMCP('hr-assist')

#tools
#resouces
#prompts

employee_manager = EmployeeManager()
leave_manager = LeaveManager()
ticcket_manager = TicketManager()
meeting_manager = MeetingManager()

email_sender = EmailSender(smtp_server="smtp.gmail.com",
                           port=587,
                           username=os.getenv("CB_EMAIL"),
                            password=os.getenv("CB_EMAIL_PWD"),
                            use_tls=True)

seed_services(employee_manager, leave_manager, meeting_manager, ticcket_manager)

@mcp.tool()
def add_employee(emp_name: str, manager_id: str, email:str) -> str:
    """Add a new employee to the system.
    Args:
        emp_name (str): Name of the new employee.
        manager_id (str): Employee ID of the manager.
        email (str): Email address of the new employee.
    Returns:
        str: Confirmation message with the new employee ID.
    """
    
    emp = EmployeeCreate(
        emp_id=employee_manager.get_next_emp_id(),
        name=emp_name,
        manager_id=manager_id,
        email=email
    )
    employee_manager.add_employee(emp)
    return f"Employee '{emp_name}' added with ID {emp.emp_id}."
    
@mcp.tool()
def get_employee_details(name: str) -> str:
    """
    Get details of an employee by name.
    Args:
        name (str): Name of the employee to search for.
    Returns:
        str: Employee details or not found message.
    """
    

    try:
        matches = employee_manager.search_employee_by_name(name)
        if not matches:
            return f"No employee found matching the name '{name}'."
        emp_id = matches[0]
        details = employee_manager.get_employee_details(emp_id)
        return f"Employee Details: ID: {emp_id}, Name: {details['name']}, Manager ID: {details['manager_id']}, Email: {details['email']}"
    except ValueError as e:
        return str(e)
    

@mcp.tool()
def send_email(subject: str, body: str, to_emails: List[str]) -> str:
    """
    Send an email using the EmailSender service.
    Args:
        subject (str): Subject of the email.
        body (str): Body content of the email.
        to_emails (List[str]): List of recipient email addresses.
    Returns:
        str: Confirmation message.
    """
    try:
        email_sender.send_email(
            subject=subject,
            body=body,
            to_emails=to_emails,
            from_email=email_sender.username,
        )
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {str(e)}"

@mcp.tool()
def create_ticket(emp_id: str, item : str, reason: str) -> str:
    """Create a ticket for an employee.
    Args:
        emp_id (str): Employee ID.
        item (str): Item for which the ticket is raised.
        reason (str): Reason for raising the ticket.
    
    Returns: str: Confirmation message.
    """
    ticket_req = TicketCreate(
        emp_id=emp_id,
        item=item,
        reason=reason
    )
    return ticcket_manager.create_ticket(ticket_req)

@mcp.tool()
def schedule_meeting(emp_id: str, meeting_dt: datetime, topic: str) -> str:
    """Schedule a meeting for an employee.
    Args:
        emp_id (str): Employee ID.
        meeting_dt (datetime): Date and time of the meeting.
        topic (str): Topic of the meeting.
        
    Returns: str: Confirmation message.
    """
    meeting_req = MeetingCreate(
        emp_id=emp_id,
        meeting_dt=meeting_dt,
        topic=topic
    )
    return meeting_manager.schedule_meeting(meeting_req)


@mcp.prompt("onboard_employee")
def onboard_employee_prompt(emp_name: str, manager_name: str, email: str) -> str:
    return f"""Onboard a new employee with the following details:
    Name: {emp_name}
    Manager: {manager_name}
    Email: {email}
    Steps:
    - Add the employee to the HRMS system.
    - Send a welcome email to the new employee with their details.
    - Notify the manager about the new hire's onboarding.
    - Raise tickets for a new laptop, id card, and other necessary equipment.
    - Schedule an introductory meeting between the new employee and their manager tomorrow at 10 AM.
    """
    
if __name__ == '__main__':
    mcp.run(transport='stdio')