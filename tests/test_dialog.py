"""Tests untuk DialogEngine — khusus choose() pada node terminal (tanpa choices)."""

from __future__ import annotations


def test_choose_empty_choices_ends_dialog(session):
    """BUG: node tanpa choices + tanpa next → choose(0) return view()
    tanpa _end(), menyebabkan soft-lock (pending_dialog tidak lepas).

    Karakterisasi: ini harus FAIL sebelum fix diterapkan."""
    session.dialog.start("dlg_intro")

    # n1 punya choices: pilih opsi 0 → lanjut ke n2
    r = session.dialog.choose(0)
    assert session.dialog.node_id == "n2"
    assert not r.get("ended")

    # n2 punya choices: [] tanpa next — harusnya terminal
    r = session.dialog.choose(0)
    # BUG: choose(0) return view() tanpa end → pending_dialog masih aktif
    assert session.dialog.current is None, (
        "Dialog harus sudah berakhir (node n2 tanpa choices = terminal)"
    )
    assert session.state.pending_dialog is None, (
        "pending_dialog harus lepas setelah node terminal"
    )
