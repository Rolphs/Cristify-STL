import app.gui.main_gui as mg


def test_create_main_window():
    mg.dpg.create_context()
    mg.create_main_window()
    assert mg.dpg.does_item_exist("main_window")
    mg.dpg.destroy_context()
