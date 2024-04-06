NAME

::

    GENOCIDE - OTP-CR-117/19


SYNOPSIS

::

    genocide <cmd> [key=val] [key==val]
    genocide [-a] [-c] [-d] [-h] [-v]


DESCRIPTION

::

    GENOCIDE holds evidence that king netherlands is doing a genocide, a
    written response where king netherlands confirmed taking note of 
    “what i have written”, namely proof that medicine he uses in
    treatement laws like zyprexa, haldol, abilify and clozapine are
    poison that make impotent, is both physical (contracted muscles)
    and mental (make people hallucinate) torture and kills members
    of the victim groups. 

    GENOCIDE contains correspondence with the International Criminal Court,
    asking for arrest of the king of the netherlands, for the genocide
    he is committing with his new treatement laws. Current status is
    "no basis to proceed" judgement of the prosecutor which requires a
    "basis to prosecute" to have the king actually arrested.


INSTALL


::

    $ pipx install genocide


USAGE

::

    without any argument the bot does nothing

    $ genocide
    $

    see list of commands

    $ genocide cmd
    cfg,cmd,mre,now,pwd

    the cfg command configures irc

    $ genocide cfg
    channel=#genocide commands=True nick=genocide port=6667 server=localhost

    start a console

    $ genocide -c 
    >

    use -v for verbose

    $ genocide -cv
    GENOCIDE started CV started Sat Dec 2 17:53:24 2023
    >

    start daemon

    $ genocided
    $ 

    show request to the prosecutor

    $ genocide req
    Information and Evidence Unit
    Office of the Prosecutor
    Post Office Box 19519
    2500 CM The Hague
    The Netherlands

    show how many died in the WvGGZ

    $ genocide now
    4y18d patient #47324 died from mental illness (14/32/11682) every 44m59s
     

CONFIGURATION


::

    irc

    $ genocide cfg server=<server>
    $ genocide cfg channel=<channel>
    $ genocide cfg nick=<nick>

    sasl

    $ genocide pwd <nsvnick> <nspass>
    $ genocide cfg password=<frompwd>

     rss

    $ genocide rss <url>
    $ genocide dpl <url> <item1,item2>
    $ genocide rem <url>
    $ genocide nme <url< <name>


COMMANDS


::

    cfg - irc configuration
    cmd - commands
    mre - displays cached output
    now - show genocide stats
    pwd - sasl nickserv name/pass
    req - reconsider
    wsd - show wisdom


SYSTEMD


::

    save the following it in /etc/systems/system/genocide.service and
    replace "<user>" with the user running pipx


    [Unit]
    Description=OTP-CR-117/19
    Requires=network-online.target
    After=network-online.target

    [Service]
    Type=simple
    User=<user>
    Group=<user>
    WorkingDirectory=/home/<user>/.genocide
    ExecStart=/home/<user>/.local/pipx/venvs/genocide/bin/genocide -d
    RemainAfterExit=yes

    [Install]
    WantedBy=default.target


    then run this

    $ mkdir ~/.genocide
    $ sudo systemctl enable genocide --now

    default channel/server is #genocide on localhost


FILES

::

    ~/.genocide
    ~/.local/bin/genocide
    ~/.local/pipx/venvs/genocide/


AUTHOR


::

    Bart Thate <bthate@dds.nl>


COPYRIGHT


::

    GENOCIDE is Public Domain.
