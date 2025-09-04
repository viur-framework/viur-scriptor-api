from .select import select
async def confirm(text: str = None, title: str = None, yes: str = "Yes", no: str = "No"):
    """
    Asks the user to answer a Yes/No Question

    :param title: the title on top of the confirm-box
    :param text: the text to be displayed
    :param yes: (optional) the word for 'yes'
    :param no: (optional) the word for 'no'
    :return:
    """
    title = title or "Confirm"
    text = text or "OK?"
    return await select(options={yes: yes, no: no}, title=title, text=text) == yes
