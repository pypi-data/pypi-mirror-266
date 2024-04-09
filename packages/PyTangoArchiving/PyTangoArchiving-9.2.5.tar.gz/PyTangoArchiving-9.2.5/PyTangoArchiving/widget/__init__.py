#__all__ = ['snaps','trend','history']
    
try:
    from . import trend
except Exception as e:
    print('Unable to import PyTangoArchiving.widget.trend: %s'%e)
    
try:
    from . import history
except Exception as e:
    print('Unable to import PyTangoArchiving.widget.history: %s'%e)


#THIS INIT FILE TRIES TO BE AS LIGHT AS POSSIBLE 

