import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


class ReportGenerator:
    def __init__(self, template_dir: str = "src/reports/templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_investment_memo(self, ticker: str, sections: dict) -> str:
        template = self.env.get_template("investment_memo.md")
        return template.render(
            ticker=ticker,
            date=date.today().isoformat(),
            **sections,
        )

    def generate_risk_report(self, ticker: str, sections: dict) -> str:
        template = self.env.get_template("risk_report.md")
        return template.render(
            ticker=ticker,
            date=date.today().isoformat(sep = ' ', timespec = 'seconds'),
            **sections,
        )

    def generate_committee_decision(self, ticker: str, hypothesis: str,
                                     agent_outputs: dict, chair_synthesis: str,
                                     recommendation: str, conviction: str,
                                     reasoning: str) -> str:
        template = self.env.get_template("committee_decision.html")
        return template.render(
            ticker=ticker,
            date=datetime.now().isoformat(sep=' ', timespec='seconds'),
            hypothesis=hypothesis,
            agent_outputs=agent_outputs,
            chair_synthesis=chair_synthesis,
            recommendation=recommendation,
            conviction=conviction,
            reasoning=reasoning,
        )

    def save(self, content: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(content)
