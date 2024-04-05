The Oasys.THIS package allows Python scripts to control the Oasys LS-DYNA Environment
software `T/HIS <https://www.oasys-software.com/dyna/software/t-his/>`_.

Basic Information
-----------------

The module uses gRPC to communicate with the T/HIS executable using the `Oasys.gRPC <https://pypi.org/project/Oasys.gRPC/>`_ module.

**The Python API is currently in Beta testing for version 21.0. If you would like to be involved in testing it then please contact dyna.support@arup.com**.

Getting started
---------------

As python is running outside T/HIS, the first thing a script needs to do is to either start an instance of T/HIS, or to connect to an already running
instance of T/HIS. At the end of the script you should then either disconnect again or terminate the T/HIS instance.

A skeleton python script to start T/HIS (Installed at C:\\Oasys 21\\this21_x64.exe) and then terminate it is::

    import Oasys.THIS

    connection = Oasys.THIS.start(abspath="C:\\Oasys 21\\this21_x64.exe")

    ...

    Oasys.THIS.terminate(connection)

By default T/HIS will use port 50052 to communicate with Python and will allocate 25Mb of memory for running scripts. These can be changed by adding port and memory arguments to the start function. e.g::

    connection = Oasys.THIS.start(abspath="C:\\Oasys 21\\this21_x64.exe", port=1234, memory=100)

T/HIS can also be started in batch mode so that the main graphics window is not shown by using a batch argument::

    connection = Oasys.THIS.start(abspath="C:\\Oasys 21\\this21_x64.exe", batch=True)
    
To connect to an instance of T/HIS that is already running, **T/HIS must currently have been started in a special mode telling it to listen on a port for gRPC messages**. 
This is done by using the ``-grpc`` command line argument when starting T/HIS. e.g::

    'C:\\Oasys 21\\this21_x64.exe' -grpc=50052

A skeleton script to connect to T/HIS and disconnect again would then be::

    import Oasys.THIS

    connection = Oasys.THIS.connect(port=50052)

    ...

    Oasys.THIS.disconnect(connection)

or if you want to terminate the instance of T/HIS use ``terminate`` instead of ``disconnect``.

Python API
----------

The JS API has been available for several years, is stable and works well, so we have designed the Python API to have the same classes, methods and properties as the JS API.
The Python API is currently in beta release and does not yet have any documentation, so for information on the available classes etc please see the `Oasys JS API documentation <https://www.oasys-software.com/dyna/downloads/oasys-suite/>`_.

However, the following classes are not available:

*   PopupWindow (GUIs not available from Python)
*   Widget (GUIs not available from Python)
*   WidgetItem (GUIs not available from Python)
*   File (use Python i/o instead)
*   Ssh (use python modules instead)
*   XlsxWorkbook (use python modules instead)
*   XlsxWorksheet (use python modules instead)
*   XMLParser (use python modules instead)
*   Zip (use python modules instead)

If an argument in the JS API is an object then the equivalent in Python will be a dict, and if an array in JS, the equivalent in Python will be a list.

Simple Example
--------------

It's probably easier to give a simple example of how to do something in T/HIS using Python compared to JavaScript, so here is simple example that opens some results and plots kinetic energy for a part using the JS API::

    var m = Model.Read("C:\\work\\test\\example.thf");

    var flag = AllocateFlag();
    ClearFlag(flag);

    m.SetFlag(flag, Entity.PART, -300000);

    var curves = m.GetDataFlagged(flag, Component.GKE);

    Plot();

and here is the equivalent example in Python::

    import Oasys.THIS

    connection = Oasys.THIS.start(abspath="C:\\oasys 21\\this21_x64.exe")

    m = Oasys.THIS.Model.Read("C:\\work\\test\\example.thf")

    flag = Oasys.THIS.AllocateFlag()
    Oasys.THIS.ClearFlag(flag)

    m.SetFlag(flag, Oasys.THIS.Entity.PART, -300000)

    curves = m.GetDataFlagged(flag, Oasys.THIS.Component.GKE)

    Oasys.THIS.Plot()
    
    Oasys.THIS.disconnect(connection)

More Information
----------------

For more details on the Oasys LS-DYNA environment software please see

* Website: `https://www.oasys-software.com/dyna/software/ <https://www.oasys-software.com/dyna/software/>`_
* Linkedin: `https://www.linkedin.com/company/oasys-ltd-software/ <https://www.linkedin.com/company/oasys-ltd-software/>`_
* YouTube: `https://www.youtube.com/c/OasysLtd <https://www.youtube.com/c/OasysLtd>`_
* Email: `dyna.support@arup.com <mailto:dyna.support@arup.com>`_
