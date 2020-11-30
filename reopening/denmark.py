from matplotlib import pyplot as plt
plt.rcParams.update({'font.size': 12})
import pandas

denmark = pandas.read_csv('denmark_data.csv', parse_dates=True, dayfirst=True)
DKr = pandas.read_csv('DK.csv')
DKr_ub = pandas.read_csv('DK-ub.csv')
DKr_lb = pandas.read_csv('DK-lb.csv')
dates = denmark['Dates']
DK_sch_dates = [dates[14], dates[47], dates[56]]
DK_other_dates = [dates[7], dates[13], dates[19], dates[20], dates[40], dates[50], dates[54]]

fig = plt.figure(figsize=(15,8))
ax = fig.gca()

# sp1
plt.subplot(121)
plt.plot(denmark['Dates'], denmark['Hospital'], "x:", lw=2, label='Observed cases')
plt.text(7.25, -1.25, 'DK-G5', rotation=0, color='k', alpha=0.5)
plt.text(13.25, 4.75, 'DK-P2', rotation=0, color='k', alpha=0.5)
plt.text(14.25, 7.75, 'DK-S3', rotation=0, color='k', alpha=0.5)
plt.text(19.25, -1.25, 'DK-R2', rotation=0, color='k', alpha=0.5)
plt.text(20.25, 1.75, 'DK-G6', rotation=0, color='k', alpha=0.5)
plt.text(40.25, .75, 'DK-R3', rotation=0, color='k', alpha=0.5)
plt.text(47.25, 19.25, 'DK-S4', rotation=0, color='k', alpha=0.5)
plt.text(47.25, 17.5, 'DK-R4', rotation=0, color='k', alpha=0.5)
plt.text(47.25, 15.75, 'DK-P3', rotation=0, color='k', alpha=0.5)
plt.text(50.25, -1.25, 'DK-P4', rotation=0, color='k', alpha=0.5)
plt.text(54.25, 0.75, 'DK-B2', rotation=0, color='k', alpha=0.5)
plt.text(56.5, 13.25, 'DK-S5', rotation=0, color='k', alpha=0.5)
for intv in DK_sch_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2)
for intv in DK_other_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2, linestyle=':')
plt.xticks(ticks=dates[::7], labels=dates[::7], rotation=45, ha='right')
#plt.xlabel('Date')
plt.ylabel('Daily hospitalisations')
plt.legend

# sp2
plt.subplot(122)
plt.plot(denmark['Dates'], DKr['V1'], "-", lw=3, label='Observed cases')
plt.plot(denmark['Dates'], DKr_lb['V1'], "b:", color='dodgerblue', lw=1)
plt.plot(denmark['Dates'], DKr_ub['V1'], "b:",color='dodgerblue', lw=1)
plt.fill_between(denmark['Dates'], DKr['V1'], DKr_lb['V1'], facecolor='dodgerblue', alpha=0.25,)
plt.fill_between(denmark['Dates'], DKr['V1'], DKr_ub['V1'], facecolor='dodgerblue', alpha=0.25,)
plt.text(7.25, -.0597, 'DK-G5', rotation=0, color='k', alpha=0.5)
plt.text(13.25, -.0577, 'DK-P2', rotation=0, color='k', alpha=0.5)
plt.text(14.25, -.0567, 'DK-S3', rotation=0, color='k', alpha=0.5)
plt.text(19.25, -.0597, 'DK-R2', rotation=0, color='k', alpha=0.5)
plt.text(20.25, -.0587, 'DK-G6', rotation=0, color='k', alpha=0.5)
plt.text(40.25, -.0587, 'DK-R3', rotation=0, color='k', alpha=0.5)
plt.text(47.25, -.0557, 'DK-S4', rotation=0, color='k', alpha=0.5)
plt.text(47.25, -.0567, 'DK-R4', rotation=0, color='k', alpha=0.5)
plt.text(47.25, -.0577, 'DK-P3', rotation=0, color='k', alpha=0.5)
plt.text(50.25, -.0597, 'DK-P4', rotation=0, color='k', alpha=0.5)
plt.text(54.25, -.0587, 'DK-B2', rotation=0, color='k', alpha=0.5)
plt.text(56.5, -.0577, 'DK-S5', rotation=0, color='k', alpha=0.5)
for intv in DK_sch_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2)
for intv in DK_other_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2, linestyle=':')
plt.ylim(-0.06,-0.02)
#plt.ylim(-0.15,0.05)
plt.xticks(ticks=dates[::7], labels=dates[::7], rotation=45, ha='right')
#plt.xlabel('Date')
plt.ylabel('Instantaneous growth rate')
plt.legend

#plt.show()
plt.tight_layout()
plt.savefig("Denmark-notes1.pdf")
