# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from tests.test_bridgepoint.utils import PrebuildFunctionTestCase
from tests.test_bridgepoint.utils import prebuild_docstring

from xtuml import navigate_one as one


class TestWhileLoop(PrebuildFunctionTestCase):

    @prebuild_docstring
    def test_while_loop(self):
        '''
        assign x = 10;
        while (x > 0)
            assign x = x - 1;
        end while;
        return x;
        '''
        act_whl = self.metamodel.select_one('ACT_WHL')
        self.assertIsNotNone(act_whl)
        
        act_smt = one(act_whl).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_whl).V_VAL[626]()
        self.assertIsNotNone(v_val)
        
        act_blk = one(act_whl).ACT_BLK[608]()
        self.assertIsNotNone(act_blk)
        
    @prebuild_docstring
    def test_while_loop_with_break(self):
        '''
        assign x = 10;
        while (x > 0)
            if (x == 5)
                break;
            end if;
            assign x = x - 1;
        end while;
        return x;
        '''
        act_whl = self.metamodel.select_one('ACT_WHL')
        self.assertIsNotNone(act_whl)
        
        act_if = one(act_whl).ACT_BLK[608].ACT_SMT[602].ACT_IF[603]()
        act_brk = one(act_if).ACT_BLK[607].ACT_SMT[602].ACT_BRK[603]()
        self.assertIsNotNone(act_brk)
        
    @prebuild_docstring
    def test_while_loop_with_continue(self):
        '''
        assign x = 10;
        while (x > 0)
            if (x == 5)
                continue;
            end if;
            assign x = x - 1;
        end while;
        return x;
        '''
        act_whl = self.metamodel.select_one('ACT_WHL')
        self.assertIsNotNone(act_whl)
        
        act_if = one(act_whl).ACT_BLK[608].ACT_SMT[602].ACT_IF[603]()
        act_con = one(act_if).ACT_BLK[607].ACT_SMT[602].ACT_CON[603]()
        self.assertIsNotNone(act_con)
        
        
if __name__ == "__main__":
    import logging
    import unittest
    
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

