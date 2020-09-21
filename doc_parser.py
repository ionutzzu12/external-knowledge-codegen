import xlrd
from pprint import pprint as pp


class Function(object):

    def __init__(self,
                 index,
                 module,
                 name,
                 return_type,
                 description,
                 parameters,
                 optional_parameters,
                 method,
                 mutable,
                 result_description):

        self.index               = int(index)
        self.module              = module
        self.name                = name
        self.return_type         = return_type
        self.description         = description
        self.parameters          = [int(float(x)) for x in parameters]
        self.optional_parameters = [int(float(x)) for x in optional_parameters]
        self.method              = method
        self.mutable             = mutable
        self.result_description  = result_description
        self.id_to_ref           = {}

    def __str__(self):
        return "{}: {} ( num_args = {}, num_kwargs = {} )"\
            .format(self.index,
                    self.name,
                    len(self.parameters),
                    len(self.optional_parameters))

    def __repr__(self):
        return str(self)

    def describe_function(self, function_title=True):

        tokens      = self.description

        if function_title:
            description = [self.name]
        else:
            description = []

        for idx, token in enumerate(tokens):

            if "$" in token:
                try:
                    param = self.id_to_ref[token[1:]]
                    if idx > 0 and tokens[idx - 1] == param.name:
                        continue
                    description.append(param.name)
                except Exception:
                    print(self.id_to_ref, self.name)
                    print("Couldn't find param {} for {}".format(token,
                                                                 self.description))
                    exit(1)
            else:
                description.append(token)

        return " ".join(description)

    def to_dict(self):

        result = {
            "name": self.name,
            "index": self.index,
            "module": self.module,
            "return_type": self.return_type.to_dict(),
            "description": self.describe_function(),
            "is_method": self.method,
            "parameters": [
                param.to_dict() for param in self.parameters
            ],
            "optional_parameters": [
                param.to_dict() for param in self.optional_parameters
            ]
        }

        return result


class Argument(object):

    def __init__(self,
                 index,
                 name,
                 types,
                 description,
                 values,
                 num_args
                 ):

        self.index       = index
        self.name        = name
        self.types       = types
        self.description = description
        self.values      = values
        self.num_args    = num_args

    def __str__(self):
        return "<Arg: {} : {}>".format(self.name, str(self.types))

    def __repr__(self):
        return str(self)

    def to_dict(self):

        result = {
            "name": self.name,
            "index": self.index,
            "types": [t.to_dict() for t in self.types],
            "description": self.description,
            "values": [
                value.to_dict() for value in self.values
            ],
            "num_args": self.num_args
        }

        return result

class Category(object):

    def __init__(self, index, name, aliases):

        self.index = index
        self.name = name
        self.aliases = aliases

    def __str__(self):
        return "<Category: {}>".format(self.name)

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "name": self.name,
            "aliases": self.aliases
        }


class PyType(object):

    def __init__(self,
                 index,
                 name,
                 description,
                 subclass):

        self.index       = index
        self.name        = name
        self.description = description
        self.subclass    = subclass

    def __str__(self):
        return "<PyType: {}>".format(self.name)

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description
        }


class PyValue(object):

    def __init__(self,
                 index,
                 value,
                 description):

        self.index       = index
        self.value       = value
        self.description = description

    def __str__(self):
        return "<PyValue: {}>".format(self.value)

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "index": self.index,
            "value": self.value,
            "description": self.description
        }


def process_parameters(parameters):

    parameters = str(parameters).strip()

    if len(parameters) == 0:
        parameters = []
    elif "[" in parameters:
        parameters = parameters \
            .replace("[", "").replace("]", "").strip()
        parameters = [x.strip() for x in parameters.split(",")]
    else:
        parameters = [parameters]

    if len(parameters) == 1 and len(parameters[0]) == 0:
        parameters = []

    return parameters


def parse_functions(args, sheet):

    doc_by_index, doc_by_name = {}, {}

    for row_idx in range(1, sheet.nrows):

        row = sheet.row_values(row_idx)
        if not row[0]:
            continue

        idx = str(int(row[0]))
        module = row[1].strip()
        name = row[2].strip()
        return_type = row[3].strip()
        parameters = process_parameters(row[4])
        optional_parameters = process_parameters(row[5])
        description = row[6].split()
        method = row[7]
        mutable = row[8]
        result_desc = row[9]

        function = Function(
            index=idx,
            module=module,
            name=name,
            return_type=return_type,
            description=description,
            parameters=parameters,
            optional_parameters=optional_parameters,
            method=method,
            mutable=mutable,
            result_description=result_desc
        )

        if idx in doc_by_index:
            raise Exception("Duplicate Function Index!")

        doc_by_index[idx] = function

        if name in doc_by_name:
            doc_by_name[name].append(idx)
        else:
            doc_by_name[name] = [idx]

    return doc_by_index, doc_by_name


def parse_parameters(args, sheet):

    doc_by_index, doc_by_name = {}, {}
    for row_idx in range(1, sheet.nrows):

        row = sheet.row_values(row_idx)
        if not row[0]:
            continue

        idx    = str(int(row[0]))
        name   = row[1].strip()

        types  = process_parameters(row[2])

        description = row[4].strip()
        values      = process_parameters(row[5])
        num_args    = str(row[6]).strip()

        parameter = Argument(
            index=idx,
            name=name,
            types=types,
            description=description,
            values=values,
            num_args=num_args
        )

        if idx in doc_by_index:
            raise Exception("Duplicate argument idx {}".format(idx))

        doc_by_index[idx] = parameter

        if name in doc_by_name:
            doc_by_name[name].append(idx)
        else:
            doc_by_name[name] = [idx]

    return doc_by_index, doc_by_name


def parse_types(args, sheet):

    doc_by_index, doc_by_name = {}, {}
    for row_idx in range(1, sheet.nrows):

        row = sheet.row_values(row_idx)
        if not row[0]:
            continue

        idx         = str(int(row[0]))
        name        = row[1].strip()
        description = row[2].strip()
        subclass    = row[3].strip()

        new_type = PyType(
            index=idx,
            name=name,
            description=description,
            subclass=subclass
        )

        doc_by_index[idx] = new_type
        doc_by_name[name] = new_type

    return doc_by_index, doc_by_name


def parse_constants(args, sheet):

    doc_by_index, doc_by_value = {}, {}
    for row_idx in range(1, sheet.nrows):

        row = sheet.row_values(row_idx)
        if not row[0]:
            continue

        idx   = str(int(row[0]))
        value = str(row[1])
        description = str(row[2])

        new_constant = PyValue(
            index=idx,
            value=value,
            description=description
        )

        doc_by_index[idx]   = new_constant
        doc_by_value[value] = new_constant

    return doc_by_index, doc_by_value


def parse_modules(args, sheet):

    doc_by_value = {}
    for row_idx in range(1, sheet.nrows):
        row = sheet.row_values(row_idx)

        idx         = str(int(row[0]))
        name        = str(row[1])
        aliases     = process_parameters(row[2])
        description = str(row[3]).strip()
        category    = str(row[4]).strip()

        doc_by_value[name] = {
            "name": name,
            "aliases": aliases,
            "description": description,
            "category": category,
            "functions": []
        }

        for alias in aliases:
            doc_by_value[alias] = doc_by_value[name]

    return doc_by_value


def parse_categories(args, sheet):

    doc_by_value = {}
    for row_idx in range(1, sheet.nrows):

        row = sheet.row_values(row_idx)

        if len(str(row[0]).strip()) == 0:
            break

        idx  = str(int(row[0]))
        name = str(row[1])
        aliases = process_parameters(row[2])

        doc_by_value[name] = Category(
            index=idx,
            name=name,
            aliases=aliases
        )

    return doc_by_value


def parse_documentation(args):

    # doc = xlrd.open_workbook("./data/lang/python/documentation.xlsx")
    doc = xlrd.open_workbook("data/codegen func documentation/documentation.xlsx")

    functions  = doc.sheet_by_name('Functions')
    parameters = doc.sheet_by_name('Parameters')
    types      = doc.sheet_by_name('Types')
    constants  = doc.sheet_by_name('Constants')
    modules    = doc.sheet_by_name('Modules')
    categories = doc.sheet_by_name('Categories')

    documentation = {
        "functions": parse_functions(args, functions),
        "parameters": parse_parameters(args, parameters),
        "types": parse_types(args, types),
        "constants": parse_constants(args, constants),
        "new_functions": {},
        "modules": parse_modules(args, modules),
        "categories": parse_categories(args, categories)
    }
    functions = documentation["functions"][0]
    modules   = documentation["modules"]

    for key in documentation["parameters"][0]:
        param = documentation["parameters"][0][key]
        param.types = [
            documentation["types"][0][t]
            for t in param.types
        ]
        param.values = [
            documentation["constants"][0][v]
            for v in param.values
        ]

    for fidx in functions:
        function = functions[fidx]
        if function.module not in modules:
            modules[function.module] = {
                "name": function.module,
                "aliases": [],
                "description": "",
                "category": "",
                "functions": [function]
            }
        else:
            modules[function.module]["functions"].append(function)

        parameters = []
        for ref_id in function.parameters:
            ref = documentation["parameters"][0][str(ref_id)]
            parameters.append(ref)
            function.id_to_ref[str(ref_id)] = ref
        function.parameters = parameters

        optional_parameters = []
        for ref_id in function.optional_parameters:
            ref = documentation["parameters"][0][str(ref_id)]
            optional_parameters.append(ref)
            function.id_to_ref[str(ref_id)] = ref

        function.optional_parameters = optional_parameters

        if function.return_type and function.return_type != 'None':
            ret_type = documentation["types"][1][function.return_type]
            function.return_type = ret_type
        else:
            function.return_type = PyType(0, "None", "None", None)

    return documentation


def main():
    parse_documentation({})


if __name__ == "__main__":
    main()
