.. _faqs:

****
FAQs
****

Installation
============

PackageNotFoundError: Package missing in current linux-64 channels
------------------------------------------------------------------

The installation of ddRAGE fails with the error:

.. code-block:: bash

    me@machine:~$ conda create -n ddrage ddrage
    Fetching package metadata .........
    
    PackageNotFoundError: Package missing in current linux-64 channels: 
      - ddrage

In this case, the bioconda channel is missing.
You can either tell conda to use it with the `-c` parameter:

.. code-block:: bash

    me@machine:~$ conda create -n ddrage -c bioconda ddrage

or permanently add it to your `.condarc` as described in the `bioconda documentation <https://bioconda.github.io/#set-up-channels>`_.

|

conda: command not found
------------------------

After installing conda, the conda command is not available.
This can be due to the fact, that the path to the conda executable(s)
has not been added to the `PATH` variable.

.. attention::
   Since `conda 4.4.0 <https://github.com/conda/conda/blob/master/CHANGELOG.md#440-2017-12-20>`_ (released 2017-12-20), the recommended way to add conda to your PATH has changed.
   The following tutorial is for versions older than 4.4.0, visit the link for an up to date version.

During the installation, the script asks, if it should add a line
to the .bashrc to solve this:

.. code-block:: bash
                
    Do you wish the installer to prepend the Miniconda3 install location to PATH in your .bashrc? [yes|no]
    [no] >>>

Choose 'yes' and start a new shell or source the .bashrc. The conda executable should be available now.

You can also add the following line manually to your .bashrc:

.. code-block:: bash
                
    export PATH="/home/<user>/miniconda3/bin:$PATH"
    
Where `<user>` is your user name. If you chose a different installation
path, find the `/bin` folder in your chosen path and replace the
path with your custom path.



|


Analysis of generated reads
===========================


Many reads are removed by the analysis tool
-------------------------------------------

While this can have many reasons, most likely this is due to the fact that some analysis
tools can not handle modified FASTQ name lines.
Since ddRAGE adds annotations to the end of the name line, all reads get discarded.

To solve this, remove the annotation with the `remove_annotation` script as described in 
:doc:`the tools chapter <documentation/tools>`.
Then try the analysis using the files without annotations (with the `_noheader` suffix).

|

BBD visualization
=================

Address already in use
----------------------

Visualizing the BBD parameters using the `visualize_bbd` script does fail with the error:

.. code-block:: Bash

    (ddrage)me@machine:~$ visualize_bbd
    Traceback (most recent call last):
      File "bbd_visualization.py", line 215, in <module>
        main_standalone()
      File "bbd_visualization.py", line 219, in main_standalone
        server = Server({'/': bokeh_app}, io_loop=io_loop)
      File "/home/me/miniconda3/envs/rad/lib/python3.5/site-packages/bokeh/server/server.py", line 121, in __init__
        sockets, self._port = _bind_sockets(self._address, port)
      File "/home/me/miniconda3/envs/rad/lib/python3.5/site-packages/bokeh/server/server.py", line 60, in _bind_sockets
        ss = netutil.bind_sockets(port=port or 0, address=address)
      File "/home/me/miniconda3/envs/rad/lib/python3.5/site-packages/tornado/netutil.py", line 194, in bind_sockets
        sock.bind(sockaddr)
    OSError: [Errno 98] Address already in use

This problem occurs, when an instance of the bokeh server is already running.
Make sure you closed all browser tabs showing the visualization and retry.

If you already closed all browser windows, stop the python process visualizing the server either using 
you process management (like top or htop), by closing the terminal in which you ran `visualize_bbd` or by killing the process.
As a last resort you can also stop ALL python processes using

.. code-block:: Bash

    (ddrage)me@machine:~$ killall python

However, make sure that no other python process that you (or others) want to keep is running on your machine.


If this does not solve the problem, make sure that no other process is using port 5006.

|

ImportError: No module named 'bokeh'
------------------------------------

Starting the `visualize_bbd` script fails with the error:

.. code-block:: Bash

    (ddrage) me@machine:~$ visualize_bbd
    Traceback (most recent call last):
      File "/home/me/miniconda3/envs/ddrage/bin/visualize_bbd", line 4, in <module>
        import ddrage.tools.bbd_visualization
      File "/home/me/miniconda3/envs/ddrage/lib/python3.5/site-packages/ddrage/tools/bbd_visualization.py", line 13, in <module>
        from bokeh.application.handlers import FunctionHandler
    ImportError: No module named 'bokeh'

This means that bokeh, the plotting library used to visualize the BBD
(which is not a hard dependency of ddRAGE), needs to be installed.
Depending on the installation kind you used, install bokeh either by using conda:

.. code-block:: Bash

    (ddrage)me@machine:~$ conda install bokeh

or using pip:

.. code-block:: Bash

    (ddrage)me@machine:~$ pip install bokeh


|

ModuleNotFoundError: No module named 'tornado'
----------------------------------------------

Starting the `visualize_bbd` script fails with the error:

.. code-block:: Bash

    (ddrage) me@machine:~$ visualize_bbd 
    Traceback (most recent call last):
      File "/vol/home/me/miniconda3/envs/ddrage/bin/visualize_bbd", line 4, in <module>
        import ddrage.tools.bbd_visualization
      File "/vol/home/me/miniconda3/envs/ddrage/lib/python3.6/site-packages/ddrage/tools/bbd_visualization.py", line 11, in <module>
        from tornado.ioloop import IOLoop
    ModuleNotFoundError: No module named 'tornado'

This means, that the tornado web-server, which is required by bokeh, is
not installed. Normally it should be installed as a dependency of
bokeh. So if you are using conda try (re-)installing bokeh:

.. code-block:: Bash

    (ddrage)me@machine:~$ conda install bokeh

If you are using pip, try the same:

.. code-block:: Bash

    (ddrage)me@machine:~$ pip install bokeh

If the dependencies are not handled automatically, try installing
tornado directly:

.. code-block:: Bash

    (ddrage)me@machine:~$ pip install tornado

However, in this case you might need to install all dependencies of
bokeh this way.
