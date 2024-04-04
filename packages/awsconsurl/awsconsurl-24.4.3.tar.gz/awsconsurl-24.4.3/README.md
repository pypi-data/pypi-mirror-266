## AWS Console URL

Generates and launches an AWS console login URL in a new tab for the default browser.

### Installation

```
pip install awsconsurl
```
* This installs boto3 and Python requests. Consider you may prefer either a local installation or a virtual environment.

### Basic Command

In basic usage:
```bash
# consurl
```
This will use your **`default`** AWS profile (from *~/.aws/credentials*) to launch a console window in your default browser.

The **-h** or **--help** prints the command arguments summary and exits. Note that the help message includes the defaults as expressed in the current environment.  Example:
```bash
$ consurl -h
usage: consurl [-h] [-V] [-v] [-p PROFILE] [-o] [-a] [-s SHORT_ROLE_NAME]
               [-r ROLE_ARN] [-n NAME] [-d DURATION]

Open AWS Console in a Browser

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         Print version and exit.
  -v, --verbose         Verbose output [False]
  -p PROFILE, --profile PROFILE
                        Specify AWS profile [default]
  -o, --output          Only Print the URL [False]
  -a, --assume-role     Assume role first [False]
  -s SHORT_ROLE_NAME, --short-role-name SHORT_ROLE_NAME
                        Specify role name to assume [DefaultConsoleRole]
  -r ROLE_ARN, --role-arn ROLE_ARN
                        (optonal) full arn to assume [None]
  -n NAME, --name NAME  Session name for assume role [rkras-rkmbp.sunyocc.edu]
  -d DURATION, --duration DURATION
                        Specify session duration [3600 Sec]

-------------------------
```

The **-V** or **--version** prints the version information and exits.

The **-v** or **--verbose** flag prints debug output to *stderr* as the URL is created. 

The **-o** or **--output** flag outputs the created console login URL to *stdout*, and does not launch the URL in the users browser.

The **-p** or **--profile** arguments specify a configured aws profile to use with the command, [described below.](README.md#Selecting_Credentials)

The Remainder of the command arguments relate to (assuming a role and are described below.](README.md#Assuming_Roles)

### Selecting Credentials

**consurl** uses the AWS ***boto3*** library, and so includes the same basic behavior as ***awscli*** in using the AWS *`credentials`* file.

**consurl** will use the profile named in **AWS_PROFILE** environment varaible, or **AWS_ACCESS_KEY_ID** and **AWS_SECRET_ACCESS_KEY**. If no environment varailbes are set, **consurl** will used configured **default** profile. 

A specific profile can be selected with the **-p** *profilename>* or **--profile** *profilename* command arguments.  This is probably the most important switch for general use.
```bash
# consurl -p sandboxcreds  
```
The credentials profile named ***[sandboxcreds]*** will be used to launch the AWS console.

These credentials will be used to obtain a console login token and a console login URL is created and used to launch the AWS console.

### Assuming Roles

**consurl** is useful to open a console session with an assumed role. This can, with the correct **iam** permissions, launch a console in a different account than the users credentials.

If you would like to assume a role, and use that roles temporary credentials for the console, use the ***-a*** or ***--assume-role*** command switch.

**consurl** will assume the role defined in **AWS_ROLE_ARN** environment variable containing the full **ARN** (Amazon Resource Name) for the role.

To override this use either the **-r** *role-arn* or **--role-arn** *role-arn* switch to specify the role. This is the best methond for assuming cross-account roles:
```bash
# consurl --assume-role --role-arn arn:aws:iam::123456789012:role/MyFavoriteRole
```

Alternatively, you can use the **-s** *short-role-name* or **--short-role-name** *short-role-name*  switch. We define the short role name as the non-ARN name of the role.  The full ARN is generated for the AWS account of the users credentials.
```base
# consurl --assume-role -s MyFavoriteRole
```
For credentials from account 123456789012 will create the role ARN arn:aws:iam::123456789012:role/MyFavoriteRole

If **--assume-role** flag is used, but neither switches nor environment strings define a role ARN, one is created with the name **DefaultConsoleRole** in the account of the users credentials, and **consurl** attempts to assume that role.

If no **--assume-role** flag is used, but either **--role-arn** or **--short-role-name** are specified **consurl** will attempt to assume the role only if it is using **iam** credentials (*i.e.* the session isn't already running an assumed role or temporary credentials.)

For assumed roles ***session name*** is retrieved from the **AWS_ROLE_SESSION_NAME** environment variable, but this can be overriden with the **-n** *session-name>* or **--name** *session-name>* switch. If neither are specified a default is formed as ***[username]-[hostname]***
```bash
# consurl -a -s ITSRole -n "alice@example.org"
```
This results in an *assumed role user* of arn:aws:sts::123456789012:assumed-role/ITSRole/alice@example.org - which can assure a consistent principle to use in IAM policies.

The **-d** *seconds* or **--duration** *seconds* switch provide the duration in Seconds for the assumed role to be valid, with the default of 3600 seconds.  For Assumed roles the maximum is set in the IAM role.
