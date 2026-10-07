from src.journal import JournalEvent, PaperJournal

def test_paper_journal_round_trip(tmp_path):
    journal=PaperJournal(tmp_path / "paper.jsonl")
    event=JournalEvent("DECISION",123,"TOKEN",{"decision":"WATCH"})
    journal.append(event)
    assert journal.read()==(event,)
