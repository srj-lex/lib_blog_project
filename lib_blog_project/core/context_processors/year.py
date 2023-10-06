import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    res = datetime.date.today()
    return {"year": res.year}
