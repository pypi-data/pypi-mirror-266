from googleapiclient.discovery import build
from google.oauth2 import service_account

class GoogleSheet:

    CREDS           = None
    SERVICE         = None
    SHEET           = None
    FORMAT          = None    
    FORMAT_DEFAULT  = "JSON"
    SCOPE           = ["https://www.googleapis.com/auth/spreadsheets"]
    ERROR           = {
        "error"     : False,
        "response"  : ""
    }

    def __init__(self, key: str = "", format = FORMAT_DEFAULT):
        """
            Creates a GoogleSheet instance.
            
            Args:
                key (str)           : The path to the service account json file.
        """
        try:
            self.CREDS          = service_account.Credentials.from_service_account_file(key, scopes=self.SCOPE)
            self.SERVICE        = build("sheets", "v4", credentials=self.CREDS)
            self.SHEET          = self.SERVICE.spreadsheets()
            self.FORMAT         = format.upper()
        except Exception as e:
            self.ERROR          = {
                "error"         : True,
                "response"      : str(e)
            }

    def get(self, spreadsheetId: str = "", ranges: list = [], filter: list = None) -> dict:
        """
            Get the data from the sheet.
            
            Args:
                spreadsheetId (str) : Id google sheet.
                range (list)        : Column or row range.
                filter (list)       : filter.

            Returns:
                dict                : return list
        """
        if self.ERROR["error"]: return self.ERROR
        try:
            
            if filter != None:
                result                  = self.SHEET.values().batchGetByDataFilter(
                    spreadsheetId       = spreadsheetId, 
                    body                = {
                        "dataFilters"   : filter
                    }
                ).execute()
            else:
                result                  = self.SHEET.values().batchGet(
                    spreadsheetId       = spreadsheetId, 
                    ranges              = ranges
                ).execute()

            
            if(self.FORMAT != self.FORMAT_DEFAULT):
                return result["valueRanges"]
            
            auxReturn                   = {}

            for element in result["valueRanges"]:
                auxList                 = []
                keyElement              = element["range"].split("!")[0]
                for items in element["values"][1:]:
                    obj                 = {}
                    lenList             = len(items)
                    for index, item in enumerate(element["values"][0]):
                        obj[item]       = items[index] if lenList > index else ""    
                    auxList.append(obj)
                
                auxReturn[keyElement]   = auxList

            return auxReturn
        except Exception as e:
            self.ERROR      = {
                "error"     : True,
                "response"  : str(e)
            }
            return self.ERROR

    def add(self, spreadsheetId: str = "", range: str = "", data: dict = {}) -> dict:
        """
            Add data to the sheet.
            
            Args:
                spreadsheetId (str) : Id google sheet.
                range (str)         : Column or row range.
                data (dict)         : array data.

            Returns:
                dict                : return response of the sheet
        """
        if self.ERROR["error"]: return self.ERROR
        try:
            return self.SHEET.values().append(
                spreadsheetId    = spreadsheetId, 
                range            = range, 
                valueInputOption = "USER_ENTERED", 
                body             = {"values": data}
            ).execute()
        except Exception as e:
            self.ERROR      = {
                "error"     : True,
                "response"  : str(e)
            }
            return self.ERROR

    def update(self, spreadsheetId: str = "", range: str = "", data: dict = {}) -> dict:
        """
            Update data to the sheet.
            
            Args:
                spreadsheetId (str) : Id google sheet.
                range (str)         : Column or row range.
                data (dict)         : array data.

            Returns:
                dict                : return response of the sheet
        """
        if self.ERROR["error"]: return self.ERROR
        try:
            return self.SHEET.values().update(
                spreadsheetId    = spreadsheetId, 
                range            = range, 
                valueInputOption = "USER_ENTERED", 
                body             = {"values": data}
            ).execute()
        except Exception as e:
            self.ERROR      = {
                "error"     : True,
                "response"  : str(e)
            }
            return self.ERROR

    def delete(self, spreadsheetId: str = "", range: str = "", idSheet: str = "") -> dict:
        """
            Delete data to the sheet.
            
            Args:
                spreadsheetId (str) : Id sheet.
                range (str)         : Column or row range.
                idSheet (dict)      : id sheet.

            Returns:
                dict                : return response of the sheet
        """
        if self.ERROR["error"]: return self.ERROR
        try:
            requests                = []
            for row in sorted(map(int, range.split(":")), reverse = True):
                requests.append({
                    "deleteDimension"   : {
                        "range"         : {
                            "sheetId"   : idSheet,
                            "dimension" : "ROWS",
                            "startIndex": int(row) - 1,
                            "endIndex"  : int(row)
                        }
                    }
                })

            return self.SHEET.batchUpdate(
                spreadsheetId       = spreadsheetId, 
                body                = {
                    "requests"      : requests
                }
            ).execute()
        except Exception as e:
            self.ERROR      = {
                "error"     : True,
                "response"  : str(e)
            }
            return self.ERROR

    def info(self) -> object:
        """
            Get sheet info.

            Returns:
                object              : return sheet info
        """
        return self.SHEET.sheets()
    
    def conditional_formatting(self, spreadsheetId: str = ""):
        try:
            if self.ERROR["error"]: return self.ERROR
            return self.SHEET.batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests"                                  : [
                    {
                        "setDataValidation"                 : {
                            "range"                         : "Formulario Receta!A1:C3",
                            "rule"                          : {
                                "condition"                 : {
                                    "type"                  : "ONE_OF_RANGE",
                                    "values"                : [
                                        {"userEnteredValue" : "=Datos!$C$1:$C$777"}
                                    ]
                                },
                                "showCustomUi"              : True,
                                "strict"                    : True
                            }
                        }
                    }
                ]
            }).execute()

        except Exception as e:
            self.ERROR      = {
                "error"     : True,
                "response"  : str(e)
            }
            return self.ERROR