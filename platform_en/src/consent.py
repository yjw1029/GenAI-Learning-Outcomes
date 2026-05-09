from database import async_add_user_action
from nicegui import app, ui

CONSENT_FORM = """#### Participant Consent Form
**Project Title**: LLMs in Education

**Principal Investigator**: [Insert investigator name] ([Insert institution])

**Invitation**: Thank you for taking the time to consider volunteering in this research project conducted by [Insert institution]. The purpose of this research is to provide insights into leveraging AI for creating a more interactive and tailored learning environment.

**Procedures**: Your participation is voluntary. If you choose to participate, the study will take around 2 hours and can be completed either online or in person. You will complete a pre-course survey online, which includes a test of your coding or math skill, then proceed to participate in an online course on either Python code or game theory (researchers will assign courses). Depending on the arrangement, you may or may not have access to an AI digital learning assistant during the course. After the course, you will complete a post-course survey online. In total, your participation will take around 2 hours.

**NOTE**: Participants are not allowed to exit once they enter each stage of the course; they must complete it within the allotted time and return to the progress page. However, participants can stay on the progress page for up to 20 minutes before proceeding to the next stage. (These 20 minutes are not included in the total experiment duration.)

During the study, we plan to collect the following information about you:

- Academic rank of university
- Major
- Grade
- Class ranking
- Income range
- Perceptions and usage of large language models
- Math and programming skills
- A log of what you type and click while interacting with our online assignment platform, including course assignments and review
- A subjective account of your experience on our platform and evaluation of its features
- Your perspective on applying large language models in education

Screen recording is required to ensure that participants are not using external tools to complete course assignments. Screen recordings do not show your face. **Participants taking part remotely will be reminded at the start of the session to close any apps showing identifiable or private information and silence any notifications (e.g. email pop-ups).**

**Compensation**: All participants will receive a basic compensation of 150 RMB. Additional incentives will be provided based on the participants' performance at learning the course material, where the performance metric is defined as: 20% * score of assignment 1 * (1 + speed of assignment 1) + 30% * score of assignment 2 * (1 + speed of assignment 2). Based on the performance in the two main tasks (Assignment 1 and Assignment 2), we will conduct a ranking. The top 10% will receive an additional incentive of 200 RMB. Those ranked in the 10% to 40% range will receive an incentive of 100 RMB. The average total compensation is anticipated to be around 210 RMB.

**NOTE**: Participants are not permitted to use any outside resources to complete course assignments. If you use any outside resources (e.g., phone, internet), you will not be compensated. Any data you provided will be destroyed within 30 days.

**Benefits**: There will be no direct benefit to you as a result of participating in this study.

We hope that findings from this research will help better understand whether and how large models can aid in student learning, and also reduce inequalities in education.

**Risks**: The risks of participating are similar to what you might experience while performing everyday tasks. Risks include fatigue, test-taking anxiety, or discomfort answering sensitive questions. You are free to skip any questions you prefer not to answer. After your information is deidentified, there is a potential for individuals to be reidentified based on unique characteristics in the data, but we are taking several precautions to prevent this, including the following: We will not share screen recordings outside of the study team, we will report findings in aggregate (individual responses are grouped together to show patterns), and we will label records with a code instead of your name.

**Privacy & Confidentiality**: Researchers will keep your participation and the information you share as confidential as possible.

The information you share, including screen recordings, will be labeled in our records with a code instead of your name or other direct identifier. The key to this code will be stored separately and destroyed after data collection is complete.

Screen recordings will be retained until we have verified that no outside resources were used to complete study tasks, after which they will be deleted. This will be completed by the time the final writeup of the study is concluded, or within two years, whichever is sooner.

Researchers may share the results of this study publicly, such as in journal articles or conference presentations, but your identity will not be disclosed.

Information collected during this study may be used for future research studies.

If you decide to withdraw from the study, and want researchers to remove your study information, you can contact the team at [[Insert contact email]]([Insert contact email]), we will delete your screen recordings, responses to the questionnaire (including details such as university rankings, major, grade, class ranking, income range, perceptions and usage of large language models, answers from math and programming skills tests, a subjective account of your experience on our platform and evaluation of its features, and your perspective on applying large language models in education), and records of interactions with the platform within 2 work days. However, once we publish the research findings in journal articles or conference presentations, it will no longer be possible to remove your information from the displayed results. The research outcomes are reported as aggregate results (combining individual responses to showcase outcomes), ensuring your personal information is not disclosed.

**Conflict of Interest Disclosure**: This research project receives sole funding from [Insert institution].

**Participation is your choice**: You participation is voluntary. Whether or not you participate is entirely up to you. You can decide to participate now and stop participating later. Your decision of whether or not to participate will have no impact on any other services or agreements you have with [Insert institution] outside of this research.

**Questions or Concerns**: If you have any questions or concerns about this study at any time, you may contact the research team at [[Insert contact email]]([Insert contact email]). If you have any questions about your rights as a research participant, please contact the [Insert institution] Institutional Review Board (IRB) at [[Insert contact email]]([Insert contact email]).

**Consent**: Would you like to participate in this study as described above?
"""


class ConsentPageBuilder:
    def __init__(self, cfg, user=None):
        self.cfg = cfg
        self.user = user
        self.username = user.get("username")

    def build(self):
        async def submit_consent():
            if radio1.value == "Yes, I would like to participate.":
                await async_add_user_action(
                    username=self.username, action="consent", value={"agree": True}
                )
                ui.navigate.to("/progress")
            elif radio1.value == "No, thanks.":
                app.storage.user.clear(), ui.navigate.to("/login")
            else:
                ui.notify("Please select an option", color="negative")

        with ui.column().classes(
            "w-full grid grid-cols-12"
        ):  # .classes("w-full h-screen grid grid-cols-11") as col:
            with ui.column().classes(
                "grid grid-cols-12 col-start-2 col-end-11 bg-white rounded-lg shadow-lg py-8"
            ):
                with ui.column().classes("col-start-2 col-end-12"):
                    ui.markdown(CONSENT_FORM)
                with ui.column().classes("col-start-2 col-end-12"):
                    radio1 = ui.radio(["Yes, I would like to participate.", "No, thanks."])

                with ui.column().classes("col-start-2 col-end-12"):
                    ui.html("""If you would like to keep a copy of this consent form, please print or save one now.""")

                with ui.column().classes("col-start-2 col-end-12"):
                    ui.button("Submit", on_click=submit_consent)
