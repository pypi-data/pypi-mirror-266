dkist-processing-ops
--------------------
|codecov|

This repository works in concert with `dkist-processing-core <https://pypi.org/project/dkist-processing-core/>`_ and
`dkist-processing-common <https://pypi.org/project/dkist-processing-common/>`_ to provide workflows for the
operational management and smoke testing of the `Automated Processing <https://nso.atlassian.net/wiki/spaces/DPD/pages/3671451/04+-+Automated+Processing>`_ stack.


Developer Setup
~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install -e .[test]
    pip install pre-commit
    pre-commit install


.. |codecov| image:: https://codecov.io/bb/dkistdc/dkist-processing-ops/branch/main/graph/badge.svg
   :target: https://codecov.io/bb/dkistdc/dkist-processing-ops
