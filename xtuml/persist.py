# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Serialize xtuml models and its schema to an sql-based file format and persist
to disk.
'''

import uuid
import logging

import xtuml


logger = logging.getLogger(__name__)


def serialize_value(value, ty):
    '''
    Serialize a value from an xtuml metamodel instance.
    '''
    ty = ty.upper()
    
    null_value = {
        'BOOLEAN'   : False,
        'INTEGER'   : 0,
        'REAL'      : 0.0,
        'STRING'    : '',
        'UNIQUE_ID' : 0
    }
    
    transfer_fn = {
        'BOOLEAN'     : lambda v: '%d' % int(v),
        'INTEGER'     : lambda v: '%d' % v,
        'REAL'        : lambda v: '%f' % v,
        'STRING'      : lambda v: "'%s'" % v.replace("'", "''"),
        'UNIQUE_ID'   : lambda v: '"%s"' % uuid.UUID(int=v)
    }

    if value is None:
        value = null_value[ty]
    
    return transfer_fn[ty](value)
    
    
def serialize_instance(instance):
    '''
    Serialize an *instance* from a metamodel.
    '''
    attr_count = 0
    metaclass = instance.__metaclass__
    s = 'INSERT INTO %s VALUES (' % metaclass.kind
    for name, ty in metaclass.attributes:
        value = getattr(instance, name)
            
        s += '\n    '
        s += serialize_value(value, ty)

        attr_count += 1
        if attr_count < len(metaclass.attributes):
            s += ', -- %s : %s' % (name, ty)
        else:
            s += ' -- %s : %s' % (name, ty)

    s += '\n);\n'

    return s


def serialize_instances(metamodel):
    '''
    Serialize all instances in a *metamodel*.
    '''
    s = ''
    for inst in metamodel.instances:
        s += serialize_instance(inst)
    
    return s


def serialize_association_link(lnk):
    '''
    Serialize an xtuml metamodel association link.
    '''
    s = '%s %s (%s)' % (lnk.cardinality.upper(),
                        lnk.kind,
                        ', '.join(lnk.ids))
    
    if lnk.phrase:
        s += " PHRASE '%s'" % lnk.phrase
        
    return s


def serialize_association(ass):
    '''
    Serialize an xtuml metamodel association.
    '''
    source = serialize_association_link(ass.source)
    target = serialize_association_link(ass.target)
    return 'CREATE ROP REF_ID %s FROM %s TO %s;\n' % (ass.id,
                                                      source,
                                                      target)


def serialize_class(Cls):
    '''
    Serialize an xtUML metamodel class.
    '''
    metaclass = Cls.__metaclass__
    attributes = ['%s %s' % (name, ty.upper()) for name, ty in metaclass.attributes]
    
    s = 'CREATE TABLE %s (\n    ' % metaclass.kind
    s += ',\n    '.join(attributes)
    s += '\n);\n'

    return s

def serialize_unique_identifiers(metamodel):
    s = ''
    
    for metaclass in metamodel.metaclasses.values():
        for index_name, attribute_names in metaclass.indices.items():
            attribute_names = ', '.join(attribute_names)
            s += 'CREATE UNIQUE INDEX %s ON %s (%s);\n' % (index_name,
                                                          metaclass.kind,
                                                          attribute_names)
    return s

def serialize_schema(metamodel):
    '''
    Serialize all class and association definitions in a *metamodel*.
    '''
    s = ''
    for kind in sorted(metamodel.metaclasses.keys()):
        s += serialize_class(metamodel.metaclasses[kind].clazz)
    
    for ass in sorted(metamodel.associations, key=lambda x: x.id):
        s += serialize_association(ass)
    
    return s


def serialize_database(metamodel):
    '''
    Serialize all instances, class definitions, association definitions, and
    unique identifiers  in a *metamodel*.
    '''
    schema = serialize_schema(metamodel)
    instances = serialize_instances(metamodel)
    identifiers = serialize_unique_identifiers(metamodel)
    
    return ''.join([schema, instances, identifiers])


def serialize(resource):
    '''
    Serialize some xtuml *resource*, e.g. an instance or a complete metamodel.
    '''
    if isinstance(resource, xtuml.MetaModel):
        return serialize_database(resource)

    elif isinstance(resource, type) and issubclass(resource, xtuml.BaseObject):
        return serialize_class(resource)
    
    elif isinstance(resource, xtuml.Association):
        return serialize_association(resource)

    elif isinstance(resource, xtuml.AssociationLink):
        return serialize_association_link(resource)
    
    elif isinstance(resource, xtuml.BaseObject):
        return serialize_instance(resource)


def persist_instances(metamodel, path):
    '''
    Persist all instances in a *metamodel* by serializing them and saving to a 
    *path* on disk.
    '''
    with open(path, 'w') as f:
        for inst in metamodel.instances:
            s = serialize_instance(inst)
            f.write(s)


def persist_schema(metamodel, path):
    '''
    Persist all class and association definitions in a *metamodel* by 
    serializing them and saving to a *path* on disk.
    '''
    with open(path, 'w') as f:
        for kind in sorted(metamodel.metaclasses.keys()):
            s = serialize_class(metamodel.metaclasses[kind].clazz)
            f.write(s)
            
        for ass in sorted(metamodel.associations, key=lambda x: x.id):
            s = serialize_association(ass)
            f.write(s)


def persist_unique_identifiers(metamodel, path):
    '''
    Persist all unique identifiers in a *metamodel* by serializing them and
    saving to a *path* on disk.
    '''
    with open(path, 'w') as f:
        for metaclass in metamodel.metaclasses.values():
            for index_name, attribute_names in metaclass.indices.items():
                attribute_names = ', '.join(attribute_names)
                s = 'CREATE UNIQUE INDEX %s ON %s (%s);\n' % (index_name,
                                                              metaclass.kind,
                                                              attribute_names)
                f.write(s)


def persist_database(metamodel, path):
    '''
    Persist all instances, class definitions and association definitions in a
    *metamodel* by serializing them and saving to a *path* on disk.
    '''
    with open(path, 'w') as f:
        for kind in sorted(metamodel.metaclasses.keys()):
            metaclass = metamodel.metaclasses[kind]
            s = serialize_class(metaclass.clazz)
            f.write(s)
            
            for index_name, attribute_names in metaclass.indices.items():
                attribute_names = ', '.join(attribute_names)
                s = 'CREATE UNIQUE INDEX %s ON %s (%s);\n' % (index_name,
                                                              metaclass.kind,
                                                              attribute_names)
                f.write(s)
                
        for ass in sorted(metamodel.associations, key=lambda x: x.id):
            s = serialize_association(ass)
            f.write(s)

        for inst in metamodel.instances:
            s = serialize_instance(inst)
            f.write(s)
