# Change Log

This is the Python Agent for AppDynamics.

## [24.2.0.6567] - 2024-02-28
### Added
 - PYTHON-1482 Adding Pytests for container id
 - PYTHON-1498 openai 1.x support for completion api's

### Fixed
 - PYTHON-1423 Cluster Agent APM Correlation CGroupv2
 - PYTHON-1423 Cluster Agent APM Correlation CGroupv2
 - PYTHON-1520 fixing container id issue on EKS


## [23.10.0.6327] - 2023-10-30
### Added
 - PYTHON-1447 added Config based instrumentation for openai sdk
 - PYTHON-1402 Option to configure TLS version 1.3


## [23.8.0.6197] - 2023-08-29
### Added
 - PYTHON-1415 added openai sdk support for python agent

### Fixed
 - PYTHON-1431 vulnerable components in python agent 23.7.0.6112


## [23.7.0.6112] - 2023-07-24
### Added
 - PYTHON-1227 added support for python 3.11
 - PYTHON-1234 added unbundled jre support for python agent
 - PYTHON-1395 Creating new pipeline for build Agent without Jre

### Fixed
 - PYTHON-1369 removed dockerhub credentials
 - PYTHON-1398 Fixing without jre pipelines and adding support for artifactory


## [23.5.0.5932] - 2023-05-05
### Fixed
 - PYTHON-1170 secret leaks in python agent repo
 - PYTHON-1191 Fix Signal Exception in newer version of python
 - PYTHON-1251 Publish Python Agent download experience artifacts to artifactory for download portal release
 - PYTHON-1259 added python-agent-init dockerfile for dockerhub support
 - PYTHON-1327 Fix MIDC wrong method info issue


## [22.10.0.5500] - 2022-10-21
### Fixed
 - PYTHON-1164/SERVER-8797 Python Agent Java Proxy Security Vulnerability in version v22.8


## [22.8.0.5306] - 2022-08-30
### Fixed
 - PYTHON-1127 cx_oracle Session Pool Interception
 - PYTHON-1144 Dual hostname on CX oracle for same argument and key arguments
 - PYTHON-1142 django interceptor bug for the addition kwargs added after Django 3.1.a1
 - PYTHON-1145 update bindeps version for release 22.8.0


## [22.7.0.5224] - 2022-07-19

## [22.5.0.5124] - 2022-05-09
### Fixed
 - PYTHON-1095 fix bug that creates dependency on /tmp/appd dir


## [22.4.1.5086] - 2022-04-27
### Fixed
 - PYTHON-1092 update bindeps version for release 22.4.0


## [22.4.0.5083] - 2022-04-27
### Added
 - PYTHON-1059 add support for python 3.10

### Fixed
 - PYTHON-1091 changed psycopg version for pytests


## [22.3.0.4990] - 2022-03-30

## [22.2.0.4918] - 2022-02-25
### Fixed
 - PYTHON-1042 fix instrumentaion issue in case of gevent
 - PYTHON-1049 fix blank username and password error in case of cx_Oracle
 - PYTHON-1045 upgrade xercesj and jackson-databind version


## [22.1.1.4847] - 2022-01-27
### Added
 - PYTHON-965 add support for fastapi framework


## [22.1.0.4756] - 2022-01-07
### Fixed
 - PYTHON-1013 updated java proxy which have log4j 2.17.1


## [21.12.2.4693] - 2021-12-21
### Fixed
 - PYTHON-1003 updated java proxy which have log4j 2.17.0


## [21.12.1.4628] - 2021-12-15
### Fixed
 - PYTHON-998 updated java proxy which have log4j 2.16.0


## [21.12.0.4611] - 2021-12-11
### Fixed
 - PYTHON-941 python agent error with psycopg2 exit calls
 - PYTHON-962 Python agent error detection feature is broken
 - PYTHON-996 updated java proxy version to resolve log4j vulnerability


## [21.10.0.4495] - 2021-10-27
### Added
 - PYTHON-862 remove support for python version 3.4
 - PYTHON-892 remove support for python version 3.5
 - PYTHON-913 Remove support for linux 32 bit

### Fixed
 - PYTHON-930 Slow and very slow BTs showing NORMAL user experience in Analytics


## [21.9.0.4385] - 2021-09-27
### Added
 - PYTHON-829 Added MIDC parsing capability to agent
 - PYTHON-830 Instrumenting MIDC methods according to parsed data
 - PYTHON-838 Data collector to feed Transaction Analytics
 - PYTHON-840 Add exit call details to Analytics events
 - PYTHON-831 Sending Instrumented data to the proxy
 - PYTHON-869 Adding http data to analytics event
 - PYTHON-71 Support for transaction analytics and MIDC for python agent
 - PYTHON-915 Enhance end_bt() api to accept user provided exception

### Fixed
 - PYTHON-916 IN_LIST condition not working
 - PYTHON-917 Added support for multiple MIDC on single method
 - PYTHON-902 Fixed unique host id issue in K8s environment
 - PYTHON-909 Fixed null point exception in proxy for MIDC


## [21.8.0.4284] - 2021-08-30
### Added
 - PYTHON-868 alpine support added and artifacts published to download portal and pypi

### Fixed
 - PYTHON-803 Updated proxy to include jackson and xercesImpl latest version and zmq fix for DL Agents
 - PYTHON-874 Trivy scanner reporting critical vulnerabilities from Python agent 21.6.0


## [21.6.0.3778] - 2021-06-11
### Added
 - PYTHON-513 Support for tcp communication with proxy
 - PYTHON-716: agent level changes for backend resolution improvement when service proxy is detected
 - PYTHON-735 Packs proxy separately and publish it to dockerhub for every release
 - PYTHON-756 Log shutdown message when agent stops
 - PYTHON-742  Combined Blackduck Scan for Python Agent, Bindeps and ProxySupport
 - PYTHON-764 Added log rate limiter to Agent logging
 - PYTHON-767 provided -s,--stop as an options to run script, to terminate the proxy gracefully
 - PYTHON-777 Implemented encryption for Python Agent
 - PYTHON-811 Added test cases for missing lines
 - PYTHON-750 Added third party license to the bindeps package
 - PYTHON-816 Reports Python Version to the controller
 - PYTHON-811 Added test cases for missing lines

### Fixed
 - PYTHON-706 Fixed masking in Remote Service Calls tab for pymongo
 - PYTHON-678 To generate new nodes on the controller when multiple agents are connected to the same proxy in case of node reuse.
 - PYTHON-720 Fixed some ports not getting allocated by java proxy in TCP mode
 - PYTHON-718 Fixed proxy not starting with persistent volume in k8s
 - PYTHON-515 Pushes proxy to downloadPortal on every release
 - PYTHON-737 Fixed proxy restart agent reconnection with TCP
 - PYTHON-755 Masking the controller accesskey in all the logs
 - PYTHON-772 Python agent does not report some transactions due to missing backend metrics

### Internel
 - PYTHON-833 changes bindeps version to 21.6.0


## [21.2.0.3144] - 2021-01-31
### Fixed
 - PYTHON-640 Import the Service-Proxy related fix implemented in JAVA-8878 to Python Java proxy


## [20.12.0.2867] - 2020-12-16
### Fixed
 - PYTHON-518 Adding support for cross app correlation
 - PYTHON-508 Aligned environment variables with other agents
 - PYTHON-637 Change bindeps version in build.gradle
 - PYTHON-639 Unable to find upstream app in snapshot for fast APIs with exit calls
 - PYTHON-556 To show Custom exit calls in the snapshot overview
 - PYTHON-643 Fixed the backport for environment variables and added test for the same


## [20.11.0.2783] - 2020-11-25
### Added
 - PYTHON-516 Support for proxy configuration from config file
 - PYTHON-580 Added environment variable support for defining unique host Id
 - PYTHON-579 Added support for CPython3.9

### Fixed
 - PYTHON-517 Agent matches BT rule to all methods (GET, POST, PUT, DELETE) when no HTTP method criteria is given
 - PYTHON-462 Removed host, port and query parameters from BT URL
 - PYTHON-575 Added contextvars backport and tornado 6 support for Python 3.5.2+
 - PYTHON-602 Fixed regression from PYTHON-575 - Tornado exit calls not ending properly


## [20.10.0.2579] - 2020-10-19
### Added
 - PYTHON-525 Added support for tornado 6 and updated agent to use contextvars when available
 - PYTHON-524 Added support for tormysql and tornado.http_client for tornado>=6

### Fixed
 - PYTHON-324 Report HTTP errors based on their error code
 - PYTHON-510 All BTs are represented as "/" for CherryPy framework
 - PYTHON-459 support for node Reuse


## [20.9.0.2430] - 2020-09-21
### Fixed
 - PYTHON-493 Remove all jackson jars from Python Proxy due to security vulnerability CVE-2020-24616
 - PYTHON-473 Corrected error format of Python errors in Proxy


## [20.8.0.2388] - 2020-08-25
### Fixed
 - PYTHON-244 MongoDB queries are sent as json instead of bson so java proxy could mask sensitive information


## [20.7.0.2292] - 2020-07-07
### Fixed
 - PYTHON-323 change to restore the request.header information of Content-Type which was affected on all tornado versions
 - PYTHON-228 update java proxy version to 20.7.0.30434 which resolves CVE-2019-17571 critical vulnerability


## [20.6.0] - 2020-06-21
### Changed
 - PYTHON-326 Switched to Azul-JRE

### Fixed
 - PYTHON-20 do not assume agent is installed in 'site-packages' directory


## [20.3.0] - 2020-03-27
### Changed
 - DLNATIVE-2926 change to a calendar based version scheme

### Fixed
 - PYTHON-6 avoid issues with functools.wraps on python 2
 - PYTHON-39 remove unused java library from the proxy


## [4.5.8.0] - 2019-11-08
### Added
 - PCF-139 Add support for controller certificates installed in non-standard location


## [4.5.7.0] - 2019-10-25
### Changed
 - DLNATIVE-2886 update bundled JRE to 1.8.0_212

### Fixed
 - DLNATIVE-1097 always configure agent on API init


## [4.5.6.0] - 2019-10-21
### Added
 - DLNATIVE-2797 Added support for CPython3.8

### Changed
 - DLNATIVE-2747 change to use structured logging instead of format strings
 - Removed support for Centos5 (EOL was 2017-03-31)

### Fixed
 - DLNATIVE-2814 update java proxy version to use the latest proxy which resolves known security vulnerabilities


## [4.5.5.0] - 2019-09-05
### Fixed
 - DLNATIVE-2769 redis interceptor works with redis-py versions >= 3.3.0


## [4.5.4.0] - 2019-08-12
### Fixed
 - DLNATIVE-2217 fixes snapshotting for Django's lazily loaded objects


## [4.5.3.0] - 2019-07-31
### Changed
 - DLNATIVE-2712 added automated integration tests for latest django(2.2) and flask(1.0) versions


## [4.5.2.0] - 2019-07-15
### Changed
 - DLNATIVE-2438 updated java proxy to remove dependencies on libraries with known security vulnerabilities.


## [4.5.1.0] - 2019-02-08
### Added
 - DLNATIVE-1421 Add support for CPython3.7

### Changed
 - DLNATIVE-2279 Removed support for CPython3.3 (EOL was 2017-09-29)


## [4.5.0.0] - 2018-07-11
### Changed
 - DLNATIVE-1668 Upgraded the agent versin from 4.3 to 4.5
 - BARE-1389 Migrate code sign agent used in pipeline to aws


## [4.3.18.0] - 2018-05-25
### Added
 - DLNATIVE-1577 python 2.6 deprecated


## [4.3.17.0] - 2018-03-08
### Added
 - DLNATIVE-1329 Added support for Django 2.0


## [4.3.16.0] - 2017-11-07
### Added
 - DLNATIVE-970 Auto-update changelog on release


## [4.3.14.0] - 2017-10-24
### Fixed
 - DLNATIVE-941 Allow custom cursor classes to be passed to `Connection.cursor` method in psycopg2


## [4.3.12.0] - 2017-09-14
### Fixed
 - DLNATIVE-782 Agent now continues to report metrics if Java proxy is restarted
 - DLNATIVE-830 Fix event in 'wait_for_bt_info_response' which always timed out


## [4.3.10.0] - 2017-08-28
### Changed
 - Agent reports its own version number and the proxy version to the controller
 - Exceptions in the transaction service are handled gracefully

### Fixed
 - DLNATIVE-637 Fixed crash when tornado.httpclient.fetch is passed kwargs


## [4.3.8.0] - 2017-08-10
### Added
 - Agent now installs and runs on CPython 3.5 and 3.6

### Fixed
 - Agent now runs on all CPython 2.x ABI versions on OSX
 - Fix agent install dependencies for py3 on linux


## [4.2.15.0] - 2017-03-16
### Added
 - OOTB instrumentation for cx_Oracle

### Changed
 - tornado.httpclient interceptor now works on all tornado versions >= 3.2


## [4.2.14.0] - 2017-02-22
### Added
 - Support for mysqlclient (MySQLdb on py3)

### Changed
 - tornado.web interceptor now works on all tornado versions >= 3.2

### Fixed
 - Fixed rare case of segfaults with mod_wsgi when handling raw Python frame objects
