from decimal import Decimal
import datetime
import re


class Formatter:
    """Converting values into desired format result"""

    def convert_query_result(self, query_result, rounding_columns=None, rounding_option=None, toList=False):
        result = []

        # converting result to both decimal and datetime if it's possible
        for i in range(len(query_result)):
            for col in query_result[i]:
                query_result[i][col] = self.convert_decimal(query_result[i][col])
                query_result[i][col] = self.convert_datetime(query_result[i][col])
            result.append(query_result[i])

        # rounding number in result
        if rounding_columns:
            result = self.rounding(result, rounding_columns, rounding_option)

        # converting result into a single dimension list
        if toList:
            listResult = []
            for row in result:
                listResult += list(row.values())
            return listResult

        return result

    def convert_decimal(self, value):
        """Converts inputted value into decimal format if it is possible"""

        if isinstance(value, Decimal):
            return float(value)
        return value

    def convert_datetime(self, value):
        """Converts inputted value into desired date format if it is possible"""

        if isinstance(value, datetime.datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S %Z")
        return value

    def convert_number(self, strNumber):
        """Converts inputted string into number if it's possible"""

        if len(strNumber):
            checkedStrNumber = strNumber.replace(".", "", 1)
            checkedStrNumber = checkedStrNumber.replace("-", "", 1) if checkedStrNumber[0] == "-" else checkedStrNumber
            if checkedStrNumber.isdigit():
                strNumber = round(float(strNumber), 1) if "." in strNumber else int(strNumber)
        return strNumber

    def rounding(self, query_result, column_names, option):
        """Iterats over query result and rounding all values in certain columns"""

        for row in query_result:
            for col in row:
                if col in column_names:
                    row[col] = round(row[col], option)
        return query_result

    def rgba_string_to_hex(self, rgba_string):
        """Converts RGBA string (mostly from Selenium) into hex code"""

        rgb_values = re.findall(r"\d+", rgba_string)
        r, g, b = map(int, rgb_values[:3])
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def convert_period(self, period: str) -> list[list]:
        """
        Converts period into separated date

        Args:
            period (str): the period string

        Returns:
            list[list]: the separated date

        Example:
            >>>  convert_period("2023/06/15 - 2023/06/06")
            [[2023, 6, 15], [2023, 6, 6]]
        """

        return [[int(_) if _ != "" else _ for _ in date.split("/")] for date in period.split(" - ")]

    def re_sub(self, pattern, string):
        return re.sub(pattern, "", string).strip()
