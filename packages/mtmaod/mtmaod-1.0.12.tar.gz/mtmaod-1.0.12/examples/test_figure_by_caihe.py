from  __future__ import division
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from sklearn.metrics import r2_score,mean_squared_error
matplotlib.use('Agg')
#matplotlib.use('TkAgg')
from scipy import stats


# ===========Calculate the point density==========
x = np.arange(0, 2, 0.01)
y = np.arange(0, 2, 0.01)
xy = np.vstack([x, y])
# xy = xy.T
print(xy.shape)
print(np.max(xy, axis=1))
z = stats.gaussian_kde(xy)(xy)
# # ===========Sort the points by density, so that the densest points are plotted last===========
# idx = z.argsort()
# print(len(idx))
# x, y, z = x[idx], y[idx], z[idx]

# np.savetxt('alldata.csv', label_test, delimiter=',')


label_test = x
## r2与 MSE/RMSE
r2 = r2_score(x,y)
mse = mean_squared_error(x,y)
rmse = np.sqrt(mean_squared_error(x,y))
count = np.size(y)

plt.scatter(x,y, marker = 'o', c = z, s = 20, cmap = 'jet', vmin = 0)
plt.colorbar()    #显示颜色条


index=np.where(x>0.5)[0]
EEenvelops=len(index)/len(x)
print(EEenvelops)
max_X_value= 1.75
# my_x_ticks = np.arange(0, max_X_value, 0.25/2)
my_x_ticks = np.arange(0,max_X_value, 0.2)
# my_y_ticks = np.arange(0, max_X_value, 0.25/2)
my_y_ticks = np.arange(0, max_X_value,0.2)
plt.xticks(my_x_ticks)
plt.yticks(my_y_ticks)
plt.xlim(0, max_X_value)
plt.ylim(0, max_X_value)
#
# index=[]
# for i in range(len(x)):
#     if (y[i]>(1.15 * x[i] + 0.05) or y[i] < (0.85 * x[i] - 0.05)) and y[i]>0.5 and y[i]<0.85: #超过该范围就记为异常点，可以通过exception.py
#         index.append(i)
# index=np.array(index)
# np.save('temp/index.npy',index)


#计算测试集的R2，mse、rmse
# r2 = r2_score(x,y)
# mse = mean_squared_error(x,y)
# rmse = mse **0.5
# count = np.size(y)


#plt.xlim(0, max_X_value)
#plt.ylim(0, max_X_value)

x_hat = np.arange(0,max_X_value,0.001)
plt.plot(x_hat,x_hat,color='black', linestyle='solid')
plt.plot(x_hat, 0.85 * x_hat - 0.05, color='red', linestyle='dashed')
plt.plot(x_hat, 1.15 * x_hat + 0.05, color='red', linestyle='dashed')

index = np.where(y>(1.15 * x + 0.05))[0]
above=len(index)/len(label_test)
plt.text(0.03,1.45,'{:.2f}% above EE'.format(above*100),color='black')

index = np.where(y < (0.85 * x - 0.05))[0]
below=len(index)/len(label_test)
plt.text(0.03,1.35,'{:.2f}% below EE'.format(below*100),color='black')

index = np.where(y<=(1.15 * x + 0.05))[0]#within范围内的点
y=y[index]
x=x[index]
index = np.where(y >= (0.85 * x - 0.05))[0]
withEE=len(index)/len(label_test)
print(y.shape)
print(x.shape)
print(np.max(y))
print(np.max(x))



# withEE=0.85
plt.text(0.03,1.55,'{:.2f}% within EE'.format(withEE*100),color='blue')
plt.text(0.03,1.65,'EE envelopes:±(0.05+15%)',color='black')
# plt.grid(True)
plt.xlabel("AERONET AOD",fontdict={'size': 12})
plt.ylabel("SPAODnet MODIS AOD",fontdict={'size': 12})
plt.text(0.03,1.25,'R2 = {:.2f}'.format(r2),color='blue')
plt.text(0.03,1.15,'RMSE = {:.2f}'.format(rmse),color='blue')
plt.text(0.03,1.05,'N = {}'.format(count),color='blue')
# plt.scatter(x,y,color = 'blue', s = 100, marker = '*',alpha = 0.65)
#plt.scatter(x,y,s = 20, marker = 'o', alpha = 0.6, c=z, cmap = 'Spectral_r')        #viridis是调色盘


plt.savefig('result.png',dpi=600)
plt.show()
