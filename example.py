#!/usr/bin/python

import dipy

class Car(object):
    def __init__(self, engine, dashboard_list, tic_tac, exhaust_fact, mock_me):
        print "my engine: %s" % engine
        print "my dashboards: %s" % dashboard_list
        print "my candy: %s" % tic_tac
        exhaust_fact()
        exhaust_fact()
        print "something mocked: %s" % mock_me


class Engine(object):
    def __init__(self):
        super(Engine, self).__init__()
        print "creating engine..."


class DashboardItem(object):
    def __init__(self):
        super(DashboardItem, self).__init__()
        print "creating dashboard..."


class Exhaust(object):
    def __init__(self):
        super(Exhaust, self).__init__()
        print "puff, puff!"


if __name__ == '__main__':
    con = dipy.Container(automock=True)
    con.register("engine", Engine())
    con.register("dashboard", DashboardItem)
    con.register("dashboard", DashboardItem())
    con.register("tic_tac", lambda con: "A tic-tac!")
    con.register("exhaust", Exhaust)
    con.register("car", Car)
    con.resolve(Car)
