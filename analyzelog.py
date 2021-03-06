import re
from Error_handler import ErrorHandler as EH
from iperf_exec import Iperf

class AnalyzeLog(object):
    """Class for analyze iperf log"""

    FILE_FULL = 'output_full.txt'
    FILE_OUTPUT = 'output.txt'


    def get_all_data(self, input_filename, thread_id):
        """Method retrieving all output data from iperf

            Args:
                input_filename (str): Input filename
                thread_id (str): Thread identification

            Returns:
                True if success,
                False if fail.
        """
        try:
            file_output_full = open(self.FILE_FULL, 'a')
            file_input = open(input_filename, 'r')

            file_output_full.write('\n\n****** ' + thread_id + ' ******\n')
            file_output_full.writelines(file_input)
            file_output_full.close()
            file_input.close()

            return True

        except IOError:
            EH(3011)
            return False
        except Exception as e:
            EH(3012)
            print(e)
            return False

    def get_mean_value(self, input_filename, thread_description):
        """Method retrieving mean value from input file.

            Args:
                input_filename (str): input file
                thread_description (str): Thread description.

            Returns:
                True if success,
                False if fail.
        """
        try:
            dur_time = int(Iperf.DURATION_TIME)
            dur_time_minus = (dur_time - 1)
            patterns = ['Server Report',
                        '0.0-%s' % dur_time,
                        '0.0- %s' % dur_time_minus,
                        '0.0- %s' % dur_time,
                        '0.0-%s' % dur_time_minus,
                        '0.0-%s' % (dur_time + 1),
                        '0.0-%s' % (dur_time + 2),
                        '0.0-%s' % (dur_time + 3),
                        '0.0-%s' % (dur_time + 4),
                        '0.0-%s' % (dur_time + 5)]
            rows = []
            
            with open(input_filename, 'r') as file_input:
                rows = file_input.readlines()

            endflag = False
            result = None
            search_res = None
            
            patt_count = -1
            for patt in patterns:
                patt_count += 1
                search_res = map(lambda row: row.find(patt, 0, 100), rows)
                if reduce(lambda x, y: x+y, search_res) != (-1 * len(rows)):
                    endflag = True
                    break

            if not endflag:
                raise ValueError

            pos_count = 0
            for pos in search_res:
                if pos is not -1:
                    break
                else:
                    pos_count += 1

            if patt_count is 0:
                result = self.reg_exp_analyze(rows[pos_count+1])
            else:
                result = self.reg_exp_analyze(rows[pos_count])

            if result != 'Not Found!':
                with open(self.FILE_OUTPUT, 'a') as file_output:
                    file_output.write(thread_description
                                      + '\t' + result + '\n')

            else:
                raise ValueError
            
            return True
            
        except IOError as ie:
            print(ie)
            EH(3021)
            return False
        except ValueError as ve:
            print(ve)
            EH(3022)
            return False
        except Exception as e:
            print(e)
            EH(3023)
            return False

    def reg_exp_analyze(self, row):
        """Method containing regular expression for get_mean_value method.

            Args:
                row (str): Row containing desired information

            Returns:
                result (str) if success;
                'Not found' if fail.
        """

        # ponizej 100Mbits/sec
        patch_under_100 = r'\d+\W{1}\d+\s+\w+\x2F\D{3}'
        # powyzej 100 Mbits/sec
        patch_above_100 = r'\d+\s+\w+\x2F\D{3}'
        match_under_100 = re.search(patch_under_100, row)
        match_above_100 = re.search(patch_above_100, row)

        if match_under_100 is not None:
            result = match_under_100.group()
        elif match_above_100 is not None:
            result = match_above_100.group()
        else:
            result = 'Not Found!'

        return result
