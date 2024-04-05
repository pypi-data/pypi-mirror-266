import re


class NameRedactor:
    """This is a helper class for cleaning up sensitive data that gets submitted
    by the agent. It is currently only used by the Git ingest functionality.

    The boolean fields related to this logic are found on the GitConfig. They are:
        GitConfig.git_strip_text_content,
        GitConfig.git_redact_names_and_urls,
    """

    def __init__(self, preserve_names=None):
        self.redacted_names = {}
        self.seq = 0
        self.preserve_names = preserve_names or []

    def redact_name(self, name):
        if not name or name in self.preserve_names:
            return name

        redacted_name = self.redacted_names.get(name)
        if not redacted_name:
            redacted_name = f'redacted-{self.seq:04}'
            self.seq += 1
            self.redacted_names[name] = redacted_name
        return redacted_name


def sanitize_text(text, strip_text_content):
    # NOTE: This module is used only by git, but we need to clean up Jira
    # keys out of commit messages. That's what this regex is for
    JIRA_KEY_REGEX = re.compile(r'([a-z0-9]+)[-|_|/| ]?(\d+)', re.IGNORECASE)

    if not text or not strip_text_content:
        return text

    return (' ').join(
        {f'{m[0].upper().strip()}-{m[1].upper().strip()}' for m in JIRA_KEY_REGEX.findall(text)}
    )
