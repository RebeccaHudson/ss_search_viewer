import sqlite3
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
from rpy2.robjects.vectors import DataFrame
from shutil import copyfile
import os
class MakePlots:
    def __init__(self, data_for_plot):
        self.data_for_plot = data_for_plot

    #takes the path to the plotting code...
    #currently runs from within the plots directory
    def load_rpy2_basics(self):
        #importr('motifStack')
        importr('data.table')
        rfile = open(os.path.dirname(os.path.realpath(__file__))+'/plot-code/super-min-standalone-plot.R', 'r')
        rcode = rfile.read()
        plotterpack = SignatureTranslatedAnonymousPackage(rcode, "plotterpack")
        return plotterpack 

    def get_reference_to_motif_library(self):
        robjects.r['load'](os.path.dirname(os.path.realpath(__file__))  +\
                          '/plot-code/jaspar_library.rda')
        robjects.r('motif_library <- jaspar_motif')
        reference_to_ml = robjects.r['motif_library']
        return reference_to_ml

    def make_plot(self):
        ppack = self.load_rpy2_basics()
        motif_lib_in_R = self.get_reference_to_motif_library()
        tfw = TempfileWriter()
        data_for_plot = self.data_for_plot[0]
        tmpfile = tfw.write_params_to_sqlite_tempfile(data_for_plot)
        any_r_return = ppack.handle_python_params(tmpfile, motif_lib_in_R)
        print("r returns something? " + repr(any_r_return) )
        tfw.cleanup_tempfile()


class TempfileWriter:
    def quote_if_needed(self, one_value):
      v =  str(one_value)
      if v[0].isalpha():
        return repr(v)
      if len(v) == 1:
        return repr(v)
      return v

    def connect_to_sqlite(self, name_of_db):
      connection = sqlite3.connect(name_of_db)
      return { 'cursor' : connection.cursor(), 'connection' : connection }

    def write_params_to_sqlite_tempfile(self, record_for_tmpfile):
      name_of_tmpdb = 'temper.db'
      self.name_of_tmpdb = name_of_tmpdb
      copyfile(os.path.dirname(os.path.realpath(__file__)) +\
               '/plot-code/empty-template-table.db', name_of_tmpdb)
      tempdb = self.connect_to_sqlite(name_of_tmpdb)
      tmp_record = self.prepare_params_for_insert(record_for_tmpfile)
      tblname = 'dmm_table_motif_unknown'  #it's just a tempfile; this name isn't important
      sql = 'INSERT INTO ' + tblname +\
      " (" +  ", ".join(tmp_record['headers']) + ")"+\
      "VALUES(" + ", ".join(tmp_record['values']) + ");"
      print("sql: " + sql)
      tempdb['cursor'].execute(sql)
      tempdb['connection'].commit()
      return name_of_tmpdb

    def prepare_params_for_insert(self, record_for_tempfile):
        attr_names = [];   values = [];
        for key, value in record_for_tempfile.iteritems():
            attr_names.append(key)
            values.append(self.quote_if_needed(value))
        return { 'headers' : attr_names, 'values' : values }

    def cleanup_tempfile(self):
      os.remove(self.name_of_tmpdb)




#sqlite_file = 'dtMotifMatchOutput-1.db'
#mp = MakePlots(sqlite_file)
#mp.make_plot('rs377194356')



