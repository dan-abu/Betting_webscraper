def load_xpaths(filename) -> None:
    """Reads xpaths file and sets xpath variables"""
    with open(filename, 'r') as file:
        lines = file.readlines()

    tomorrows_races_xpath = lines[0]
    self.all_race_tables_xpath = lines[1]
    self.race_table_xpath = lines[2] #use .format
    self.race_table_row_xpath = lines[3]
    self.race_table_cell_xpath = lines[4]
    self.race_table_track_name_xpath = lines[5]
    self.race_table_row_track_name_xpath = lines[6]
    self.race_category_xpath = lines[7]
    self.race_category_columns_xpath = lines[8]
    self.race_category_headers_xpath = lines[9]