import os
import unittest
import xtuml
import bridgepoint

import xtuml.consistency_check


class TestConcistency(unittest.TestCase):
    '''
    Test suite for the module xtuml.consistency_check
    '''
 
    def setUp(self):
        self.metamodel = bridgepoint.load_metamodel()

    def tearDown(self):
        del self.metamodel
        
    def test_empty_model(self):
        self.assertTrue(self.metamodel.is_consistent())
    
    def test_association_integrity(self):
        m = self.metamodel
        s_dt = m.select_one('S_DT', xtuml.where_eq(Name='string'))
        s_bparm = m.new('S_BPARM', Name='My_Parameter')
        s_ee = m.new('S_EE', Name='My_External_Entity', Key_Lett='My_External_Entity')
        pe_pe = m.new('PE_PE', Visibility=True, type=5)
        s_brg = m.new('S_BRG', Name='My_Bridge_Operation')
        
        
        self.assertEqual(1, xtuml.check_association_integrity(m, 22))
        self.assertTrue(xtuml.relate(s_bparm, s_dt, 22))
        self.assertEqual(0, xtuml.check_association_integrity(m, 22))
        
        self.assertEqual(1, xtuml.check_association_integrity(m, 21))
        self.assertTrue(xtuml.relate(s_bparm, s_brg, 21))
        self.assertEqual(0, xtuml.check_association_integrity(m, 21))
        
        self.assertEqual(1, xtuml.check_association_integrity(m, 20))
        self.assertTrue(xtuml.relate(s_brg, s_dt, 20))
        self.assertEqual(0, xtuml.check_association_integrity(m, 20))
        
        self.assertEqual(1, xtuml.check_association_integrity(m, 8001))
        self.assertTrue(xtuml.relate(s_ee, pe_pe, 8001))
        self.assertEqual(0, xtuml.check_association_integrity(m, 8001))
        
        self.assertEqual(1, xtuml.check_association_integrity(m, 19))
        self.assertTrue(xtuml.relate(s_brg, s_ee, 19))
        self.assertEqual(0, xtuml.check_association_integrity(m, 19))
        
        # the old, unused association R8 is still present in ooaofooa, and thus
        # consistency check fails on S_EE.
        #self.assertTrue(m.is_consistent())
        
    def test_unique_identifier_with_null(self):
        m = self.metamodel
        act_blk = m.new('ACT_BLK')
        act_blk.Block_ID = None
        self.assertEqual(1, xtuml.check_uniqueness_constraint(m, 'ACT_BLK'))
        
    def test_uniqueness_constraint(self):
        m = self.metamodel
        self.assertTrue(m.is_consistent())
        
        s_dt = m.select_one('S_DT', xtuml.where_eq(Name='string'))
        m.clone(s_dt)
        
        # S_DT has two unique identifiers (I1 and I2). two instances
        # produce one error each, hence 4 errors
        self.assertFalse(m.is_consistent())
        self.assertEqual(4, xtuml.check_uniqueness_constraint(m, 'S_DT'))
        
        xtuml.delete(s_dt)
        self.assertTrue(m.is_consistent())

    def test_subtype_integrity(self):
        for num in range(0, 5):
            errors = xtuml.check_subtype_integrity(self.metamodel, 'PE_PE', 8001)
            self.assertEqual(num, errors)
            self.metamodel.new('PE_PE')
        

class TestConcistencyCLI(unittest.TestCase):
    '''
    Test suite for the xtuml.consistency_check 
    command line interface.
    '''
    def main(self, *args):
        try:
            return xtuml.consistency_check.main(list(args))
        except SystemExit as e:
            return e.code
    
    def test_no_args(self):
        rc = self.main()
        self.assertEqual(1, rc)
        
    def test_ooaofooa_globals(self):
        path = (os.path.dirname(__file__) + os.sep + os.pardir + os.sep + 
                'resources' + os.sep)
                
        rc = self.main(path + 'ooaofooa_schema.sql', path + 'Globals.xtuml')
        self.assertEqual(0, rc)
        
    def test_limit_searchspace(self):
        path = (os.path.dirname(__file__) + os.sep + os.pardir + os.sep + 
                'resources' + os.sep)
                
        rc = self.main(path + 'ooaofooa_schema.sql', path + 'Globals.xtuml',
                       path + 'Globals.xtuml')
                       
        self.assertNotEqual(0, rc)
        
        rc = self.main(path + 'ooaofooa_schema.sql', path + 'Globals.xtuml',
                       path + 'Globals.xtuml', '-k', 'O_OBJ', '-r', '0')
                       
        self.assertEqual(0, rc)
        
        
