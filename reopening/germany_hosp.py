from matplotlib import pyplot as plt
plt.rcParams.update({'font.size': 12})
import pandas

germany = pandas.read_csv('germany_data_hosp.csv', parse_dates=True, dayfirst=True)
DEr = pandas.read_csv('DE.csv')
DEr_ub = pandas.read_csv('DE-ub.csv')
DEr_lb = pandas.read_csv('DE-lb.csv')
dates = germany['Dates']
DE_sch_dates = [dates[2], dates[9], dates[16]]
DE_other_dates = [dates[1], dates[13], dates[27], dates[31]]

fig = plt.figure(figsize=(15,8))
ax = fig.gca()

# sp1
plt.subplot(121)
plt.plot(germany['Dates'], germany['Hospital'], "x--", lw=2, label='Observed cases')
plt.text(1.25, -18, 'DE-G3', rotation=0, color='k', alpha=0.5)
plt.text(2.25, 18.75, 'DE-S4', rotation=0, color='k', alpha=0.5)
plt.text(2.25, 8.5, 'DE-R3', rotation=0, color='k', alpha=0.5)
plt.text(2.25, -2.25, 'DE-P5', rotation=0, color='k', alpha=0.5)
plt.text(9.25, -18, 'DE-S5', rotation=0, color='k', alpha=0.5)
plt.text(13.25, 2, 'DE-B3', rotation=0, color='k', alpha=0.5)
plt.text(16.25, -7.75, 'DE-S6', rotation=0, color='k', alpha=0.5)
plt.text(16.25, -18, 'DE-G4', rotation=0, color='k', alpha=0.5)
plt.text(27.25, -7.75, 'DE-G5', rotation=0, color='k', alpha=0.5)
plt.text(31.25, -18, 'DE-R4', rotation=0, color='k', alpha=0.5)
for intv in DE_sch_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2)
for intv in DE_other_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2, linestyle=':')
plt.xticks(ticks=dates[::7], labels=dates[::7], rotation=45, ha='right')
#plt.xlabel('Date')
plt.ylabel('Daily hospitalisations')
plt.legend

# sp2
plt.subplot(122)
plt.plot(germany['Dates'], DEr['V1'], "-", lw=3, label='Observed cases')
plt.plot(germany['Dates'], DEr_lb['V1'], "b:", color='dodgerblue', lw=1)
plt.plot(germany['Dates'], DEr_ub['V1'], "b:", color='dodgerblue', lw=1)
plt.fill_between(germany['Dates'], DEr['V1'], DEr_lb['V1'], facecolor='dodgerblue', alpha=0.25)
plt.fill_between(germany['Dates'], DEr['V1'], DEr_ub['V1'], facecolor='dodgerblue', alpha=0.25)
plt.text(1.25, -.148, 'DE-G3', rotation=0, color='k', alpha=0.5)
plt.text(2.25, -.129, 'DE-S4', rotation=0, color='k', alpha=0.5)
plt.text(2.25, -.135, 'DE-R3', rotation=0, color='k', alpha=0.5)
plt.text(2.25, -.141, 'DE-P5', rotation=0, color='k', alpha=0.5)
plt.text(9.25, -.148, 'DE-S5', rotation=0, color='k', alpha=0.5)
plt.text(13.25, -.135, 'DE-B3', rotation=0, color='k', alpha=0.5)
plt.text(16.25, -.142, 'DE-S6', rotation=0, color='k', alpha=0.5)
plt.text(16.25, -.148, 'DE-G4', rotation=0, color='k', alpha=0.5)
plt.text(27.25, -.141, 'DE-G5', rotation=0, color='k', alpha=0.5)
plt.text(31.25, -.148, 'DE-R4', rotation=0, color='k', alpha=0.5)
for intv in DE_sch_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2)
for intv in DE_other_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2, linestyle=':')
plt.ylim(-0.15,0.1)
plt.xticks(ticks=dates[::7], labels=dates[::7], rotation=45, ha='right')
#plt.xlabel('Date')
plt.ylabel('Instantaneous growth rate')
plt.legend

#plt.show()
plt.tight_layout()
plt.savefig("Germany-hospital-notes.pdf")
