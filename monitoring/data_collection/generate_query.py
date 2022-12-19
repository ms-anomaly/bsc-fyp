

class query_generator:

    def __init__(self,bucket,measurement,container_names,fields,range):
        self.bucket = bucket
        self.container_names = container_names
        self.fields = fields
        self.range = range
        self.measurement = measurement

        
    def generate_query(self,container_name,field):

        query = 'from(bucket:"'+self.bucket+'")\
            |> range(start: -'+ str(self.range)+'m)\
            |> filter(fn:(r) => r._measurement == "'+self.measurement+'")\
            |> filter(fn:(r) => r.name == "'+container_name+'")\
            |> filter(fn:(r) => r._field == "'+field+'")'