


import numpy as np
import arff
import random
import pandas as pd



class CrossValidation:



    def __init__(self,file_name,distance_func="default",file_type="arff"):
        '''
        Constructor method, setups up the the necessary class attributes to be
        used by the complexity measure functions.
        Starts by reading the file in arff format which contains the class samples X (self.X), class labels y (self.y) and contextual information
        about the features (self.meta).
        It also saves in an array the unique labels of all existing classes (self.classes), the number of samples in each class (self.class_count) and
        the indexes in X of every class (self.class_inxs).
        -----
        Parameters:
        file_name (string): Location of the file that contains the dataset.
        distance_func (string): The distance function to be used to calculate the distance matrix. Only available option right now is "HEOM".
        file_type (string): The type of file where the dataset is stored. Only available option right now is "arff".
        
        '''
        if(file_type=="arff"):
            [X,y,meta,class_inds]=self.__read_file(file_name)
        else:
            print("Only arff files are available for now")
            return

        self.X=np.array(X)
        self.y=np.array(y)
        self.classes=np.unique(self.y)
        self.meta=meta
        
        self.class_inxs = class_inds
        self.dist_matrix_per_class = self.__calculate_distance_matrix(self.X,distance_func=distance_func)
        #self.class_count = self.__count_class_instances()


       


        self.class_count = self.__count_class_instances()
        if(len(self.class_count)<2):
           print("ERROR: Less than two classes are in the dataset.")

        return 

    


    def __count_class_instances(self):
        '''
        Is called by the __init__ method.
        Count instances of each class in the dataset.
        --------
        Returns:
        class_count (numpy.array): An (Nx1) array with the number of intances for each of the N classes in the dataset 
        '''
        class_count = np.zeros(len(self.classes))
        for i in range(len(self.classes)):
            count=len(np.where(self.y == self.classes[i])[0])
            class_count[i]+=count
        return class_count


    def __read_file(self,file):
        data = arff.load(open(file, 'r'))['data']
        num_attr = len(data[0])-1
        att=arff.load(open(file, 'r'))['attributes']


        self.att = att

        meta=[]
        for i in range(len(att)-1):
            if(att[i][1]=="NUMERIC"):
                meta.append(0)
            else:
                meta.append(1)

        
        X = np.array([i[:num_attr] for i in data],dtype=object)
        y = np.array([i[-1] for i in data])


        



        '''
        for i in range(len(meta)):
            if meta[i]==1:
                
                b, c = np.unique(X[:,i], return_inverse=True)
                X[:,i] = c

        if 1 in meta:
            X = X.astype(np.float64)
        '''

        

        classes = np.unique(y)
        
        

        class_inds = []
        for cls in classes:
            cls_ind=np.where(y==cls)[0]
            class_inds.append(cls_ind)
        


        X = np.array(X,dtype=object)
        
        y = np.array(y)
        

        return [X,y,meta,class_inds]
    


    def __distance_HEOM(self,X):
        '''
        Is called by the calculate_distance_matrix method.
        Calculates the distance matrix between all pairs of points from an input matrix, using the HEOM metric, that way categorical attributes are
        allow in the dataset.
        --------
        Parameters: 
        X (numpy.array): An (N*M) numpy matrix containing the points, where N is the number of points and M is the number of attributes per point.
        --------
        Returns:
        dist_matrix (numpy.array): A (M*M) matrix containing the distance between all pairs of points in X
        '''
        
        
        meta = self.meta
        dist_matrix=np.zeros((len(X),len(X)))
        unnorm_dist_matrix = np.zeros((len(X),len(X)))

        #calculate the ranges of all attributes
        #range_max=np.max(X,axis=0)
        #range_min=np.min(X,axis=0)


        range_max = np.array([])
        range_min = np.array([])
        for attr in range(len(X[0])):
            
            if(meta[attr]==0):
                range_max = np.append(range_max,np.max(X[:,attr]))
                range_min = np.append(range_min,np.min(X[:,attr]))
            else:
                range_max = np.append(range_max,0)
                range_min = np.append(range_min,0)

        
        #print(range_max)
        #print(range_min)
        
        for i in range(len(X)): 
            for j in range(i+1,len(X)):
                #for attribute
                dist = 0
                unnorm_dist = 0
                for k in range(len(X[0])):
                    #missing value
                    if(X[i][k] == None or X[j][k]==None):
                        dist+=1
                        unnorm_dist+=1
                    #numerical
                    if(meta[k]==0):
                        #dist+=(abs(X[i][k]-X[j][k]))**2
                        
                        #dist+=(abs(X[i][k]-X[j][k])/(range_max[k]-range_min[k]))**2
                        if(range_max[k]==range_min[k]):
                            dist+=(abs(X[i][k]-X[j][k]))**2
                            unnorm_dist+=(abs(X[i][k]-X[j][k]))**2
                        else:
                            dist+=(abs(X[i][k]-X[j][k])/(range_max[k]-range_min[k]))**2
                            unnorm_dist+= abs(X[i][k]-X[j][k])**2
                            
                            #dist+=(abs(X[i][k]-X[j][k]))**2
                    #categorical
                    if(meta[k]==1):
                        if(X[i][k]!=X[j][k]):
                            dist+=1
                            unnorm_dist+=1

                dist_matrix[i][j]=np.sqrt(dist)
                dist_matrix[j][i]=np.sqrt(dist)

                unnorm_dist_matrix[i][j]=np.sqrt(unnorm_dist)
                unnorm_dist_matrix[j][i]=np.sqrt(unnorm_dist)
        #print(dist_matrix)
        return dist_matrix,unnorm_dist_matrix
    


    def __calculate_distance_matrix(self,X,distance_func="HEOM"):
        '''
        Is called by the __init__ method.
        Function used to select which distance metric will be used to calculate the distance between a matrix of points.
        Only the HEOM metric is implemented for now, however if more metrics are added this function can easily be changed to
        incomporate the new metrics.
        --------
        Parameters:
        X (numpy.array): An (N*M) numpy matrix containing the points, where N is the number of points and M is the number of attributes per point.
        distance_func (string): The distance function to be used, only available option right now is "HEOM"
        --------
        Returns:
        dist_matrix (numpy.array): A (M*M) matrix containing the distance between all pairs of points in X
        --------
        '''

        dist_matrix_per_class = []
        if(distance_func=="HEOM"):
            

            for c_count in range(len(self.classes)):
                X_cls = self.X[self.class_inxs[c_count]]
                dist_matrix_cls,unnorm_dist_matrix_cls = self.__distance_HEOM(X_cls)
                dist_matrix_per_class.append(dist_matrix_cls)


        elif(distance_func=="default"):
            for c_count in range(len(self.classes)):
                X_cls = self.X[self.class_inxs[c_count]]
                dist_matrix_cls,unnorm_dist_matrix_cls = self.__distance_HEOM(X_cls)
                dist_matrix_per_class.append(dist_matrix_cls)
        
        #add other distance functions
        
        return dist_matrix_per_class
    
    
    def __write_arff(self,X_res,y_res,output_folder,file):
        '''
        Called by write_folds to write a partition into a file.
        -----
        Parameters:
        X_res (np.array): An array containing the samples
        y_res (np.array): An array containing the labels of the samples in X
        output_folder (str): The name to save the partition under
        file (str): the folder the files will be saved on
        '''


        X_res = pd.DataFrame(X_res)
       
        y_res = pd.DataFrame(y_res)
        

        
        
        
        
        y_res.rename(columns = {0 : 'class'}, inplace = True)
        df =  X_res.join(y_res)

        #print(df)
        #attributes = [(str(j), 'NUMERIC') if X_res[j].dtypes in ['int64', 'float64'] else (j, X_res[j].unique().astype(str).tolist()) for j in X_res]
        #attributes += [('label',['0.0','1.0'])]


        attributes = self.att

        arff_dic = {
                'attributes': attributes,
                'data': df.values,
                'relation': 'myRel',
                'description': ''
                }
        #print(arff_dic)
        
        #new_name = file.split(".")[0]  + ".arff"
        with open(output_folder + file + ".arff", "w", encoding="utf8") as f:
            arff.dump(arff_dic, f)

    def write_folds(self,folds,folds_y,filename,folder):
        '''
        Function used to write the folds to arff files, it will create the n training and testing partitions, where n is lenght of folds array passed as parameter.
        -------
        Parameters:
        folds (numpy.array): An array of arrays contaning the n folds to be saved to the file
        folds_y (numpy.array): An array of arrays containing the labels of the samples in each fold
        filename (str): The filename the partitions will be saved under. Each partition will contain a suffix in from of the filename to indentify it. For example, assuming 5 folds, the first train partition will be
        saved under "filename-5-1tra.arff" and the first test partition under "filename-5-1tst.arff"
        folder (str): the folder the files will be saved on
        --------
        Returns:
        dist_matrix (numpy.array): A (M*M) matrix containing the distance between all pairs of points in X
        
        
        '''



        training_partitions = []
        testing_partitions = []

        #n partitions will be generated. n is equal to the number of folds. Each partition will have n-1 folds for training and the remaining fold will be used for testing.
        for i in range(len(folds)):

            train_fold_X=[]
            test_fold_X = np.array(folds[i])

            train_fold_y=[]
            test_fold_y= np.array(folds_y[i])

            for j in range(len(folds)):

                if(j!=i):
                    
                    if(len(train_fold_X)==0):
                        train_fold_X = folds[j]
                        train_fold_y = folds_y[j]
                    else:
                        train_fold_X = np.append(train_fold_X,folds[j],axis=0)
                        train_fold_y = np.append(train_fold_y,folds_y[j])


            training_partitions.append(train_fold_X)
            testing_partitions.append(test_fold_X)

            #name_tra = file.split(".")[0] + "-" + cv_algorithm +"-V" + str(v) + "-" + str(fold_num) + "-" + str(i+1) + "tra.arff" 
            #name_tst = file.split(".")[0] + "-" + cv_algorithm +"-V" + str(v) + "-" + str(fold_num) + "-" + str(i+1) + "tst.arff" 

            #make the new file name for each partition
            name_tra = filename + "-" + str(len(folds)) + "-" + str(i+1) + "tra"
            name_tst = filename + "-" + str(len(folds)) + "-" + str(i+1) + "tst"

            #write the partitions to files
            self.__write_arff(train_fold_X,train_fold_y,folder,name_tra)
            self.__write_arff(test_fold_X,test_fold_y,folder,name_tst)
    


    def getClosest(self,pos,dist_matrix):
        '''
        Gets the closest sample to the one passed as parameter according to a distance matrix.
        ------
        Parameters:
        pos (int): The position of the sample in the distance matrix
        distance_matrix (np.array): An NxN distance matrix containing the distances from each samples to all others. Row n correponds the distance of sample n to all other samples.
        ------
        Returns:
        new_pos(int): The position of the closest sample
        
        '''
        #select closest sample 
        #in case of the first row the value has to be different
        if(pos!=0):
            min_val = dist_matrix[pos][0]
            new_pos = 0
        else:
            min_val = dist_matrix[pos][1]
            new_pos = 1
        

        for i in range(len(dist_matrix[pos])):
            #check if not itself
            if i!=pos:
                if dist_matrix[pos][i] < min_val:
                    min_val = dist_matrix[pos][i]
                    new_pos = i
            #get min


        #remove sample from dist matrix
        return new_pos
    


    def getMostDistant(self,pos,dist_matrix):
        '''
        Gets the most distant sample to the one passed as parameter according to a distance matrix.
        ------
        Parameters:
        pos (int): The position of the sample in the distance matrix
        distance_matrix (np.array): An NxN distance matrix containing the distances from each samples to all others. Row n correponds the distance of sample n to all other samples.
        ------
        Returns:
        new_pos (int): The position of the most distant sample
        
        '''
        #select closest sample 
        #in case of the first row the value has to be different
        if(pos!=0):
            min_val = dist_matrix[pos][0]
            new_pos = 0
        else:
            min_val = dist_matrix[pos][1]
            new_pos = 1
        

        for i in range(len(dist_matrix[pos])):
            #check if not itself
            if i!=pos:
                if dist_matrix[pos][i] > min_val:
                    min_val = dist_matrix[pos][i]
                    new_pos = i
            #get min


        #remove sample from dist matrix
        return new_pos


    def SCV(self,foldNum=5):
        '''
        Function used to perform statified cross validation (SCV), each fold will contain the same number of samples of each class, which
        makes sure to mitigate prior probability dataset shift. 
        ------
        Parameters:
        foldNum (int): Number of folds to split the dataset into. Default value of 5 folds.
        ------
        Returns:
        folds (numpy.array): An array of foldNum size containing the split dataset according to SCV. Each element of this array corresponds to a fold.
        folds_y (numpy.array): An array of foldNum size containing the class labels for the samples in each fold of the fold array. 
        folds_inx (numpy.array): An array of foldNum size containing the indexes of the samples (in relation to the complete dataset) in each fold of the fold array.
        '''
        folds = []
        folds_y = []
        folds_inx = []

        for i in range(foldNum):
            folds.append([])
            folds_y.append([])
            folds_inx.append([])


        class_inxs = self.class_inxs
        
        #for each class
        for c_count in range(len(self.classes)):
            X_cls = self.X[class_inxs[c_count]]
            y_cls = self.y[class_inxs[c_count]]
            cls_inxs = class_inxs[c_count]


            orgCount = len(cls_inxs)
            for i in range(foldNum):
                
                #number of samples per fold (each fold will have almost same number of samples)
                n = orgCount//foldNum
                for j in range(0,n):

                    #select a random sample
                    pos = random.randint(0,len(X_cls)-1)
                    

                    #assign sample to fold
                    folds[i].append(X_cls[pos])
                    folds_y[i].append(y_cls[pos])
                    folds_inx[i].append(cls_inxs[pos])
                    

                    #delete assigned samples to make sure no duplicate samples are assigned
                    X_cls = np.delete(X_cls, (pos), axis=0)
                    y_cls = np.delete(y_cls, (pos), axis=0)
                    cls_inxs = np.delete(cls_inxs, (pos), axis=0)


                #adress the extra samples that can't be divided evenly
                if(orgCount%foldNum>i):


                    pos = random.randint(0,len(X_cls)-1)

                    folds[i].append(X_cls[pos])
                    folds_y[i].append(y_cls[pos])
                    folds_inx[i].append(cls_inxs[pos])

                    X_cls = np.delete(X_cls, (pos), axis=0)
                    y_cls = np.delete(y_cls, (pos), axis=0)
                    cls_inxs = np.delete(cls_inxs, (pos), axis=0)
                

        return folds,folds_y,folds_inx

           



    def DBSCV(self,foldNum=5):
        '''
        Function used to perform distribution balanced statified cross validation (DBSCV) [1], each fold will contain the same number of samples of each class, which
        makes sure to mitigate prior probability dataset shift. Additionally, this method also tries to mitigate covariate shift by assigning the samples from the 
        feature space evenly in each fold.
        ------
        Parameters:
        foldNum (int): Number of folds to split the dataset into. Default value of 5 folds.
        ------
        Returns:
        folds (numpy.array): An array of foldNum size containing the split dataset according to SCV. Each element of this array corresponds to a fold.
        folds_y (numpy.array): An array of foldNum size containing the class labels for the samples in each fold of the fold array. 
        folds_inx (numpy.array): An array of foldNum size containing the indexes of the samples (in relation to the complete dataset) in each fold of the fold array.
        ------
        References:
        [1] Xinchuan Zeng and Tony R. Martinez. Distribution-balanced stratified cross-validation for accuracy estimation. Journal of Experimental & Theoretical Artificial Intelligence,
        12(1):1–12, 2000. doi: 10.1080/095281300146272. URL https://doi.org/10.1080/095281300146272.5
        '''
        folds = []
        folds_y = []
        folds_inx = []
        

        class_inxs = self.class_inxs
       
        
        for i in range(foldNum):
            folds.append([])
            folds_y.append([])
            folds_inx.append([])

        #for each class
        for c_count in range(len(self.classes)):
            X_cls = self.X[class_inxs[c_count]]
            y_cls = self.y[class_inxs[c_count]]
            cls_inxs = class_inxs[c_count]

            #get the distant matrix for the current class
            dist_matrix_cls = self.dist_matrix_per_class[c_count]
                
            i = 0
            cnt=len(X_cls)
            

            #select first position
            pos = random.randint(0,len(X_cls)-1)
            sample = X_cls[pos]
            sample_y = y_cls[pos]


            #while there still are samples left
            while(cnt>1): 
                #assign sample
                folds[i].append(sample)
                folds_y[i].append(sample_y)
                folds_inx[i].append(cls_inxs[pos])
                
                
                
                cnt = cnt-1

                #rotate through the folds at each iteration
                i = (i+1)%foldNum


                #remove from dataset
                X_cls = np.delete(X_cls, (pos), axis=0)
                y_cls = np.delete(y_cls, (pos), axis=0)
                cls_inxs = np.delete(cls_inxs, (pos), axis=0)


                #get the next sample, which is the closest in distance to the current fold
                new_pos = self.getClosest(pos,dist_matrix_cls)
                

                #remove form dist matrix
                dist_matrix_cls = np.delete(dist_matrix_cls, (pos), axis=0)
                dist_matrix_cls = np.delete(dist_matrix_cls, (pos), axis=1)
                

                if(new_pos > pos):
                    pos = new_pos-1
                else:
                    pos = new_pos


                #new sample
                sample = X_cls[pos]
                sample_y = y_cls[pos]

            #assign the last sample
            folds[i].append(sample)
            folds_y[i].append(sample_y)        
            folds_inx[i].append(cls_inxs[pos])    

        return folds,folds_y,folds_inx
    
    def DOBSCV(self,foldNum=5):
        '''
        Function used to perform distribution optimized balanced statified cross validation (DOBSCV) [1], each fold will contain the same number of samples of each class, which
        makes sure to mitigate prior probability dataset shift. Additionally, this method also tries to mitigate covariate shift by assigning the samples from the 
        feature space evenly in each fold. DOBSCV is less sensitive to random choices since, after assigning a sample to each of the folds, it picks a new random
        sample to restart the process.
        ------
        Parameters:
        foldNum (int): Number of folds to split the dataset into. Default value of 5 folds.
        ------
        Returns:
        folds (numpy.array): An array of foldNum size containing the split dataset according to SCV. Each element of this array corresponds to a fold.
        folds_y (numpy.array): An array of foldNum size containing the class labels for the samples in each fold of the fold array. 
        folds_inx (numpy.array): An array of foldNum size containing the indexes of the samples (in relation to the complete dataset) in each fold of the fold array.
        ------
        References:
        [1] Jose Garcıa Moreno-Torres, Jose A. Saez, and Francisco Herrera. Study on the impact of
        partition-induced dataset shift on k-fold cross-validation. IEEE Transactions on Neural
        Networks and Learning Systems, 23(8):1304–1312, 2012b. doi: 10.1109/TNNLS.2012.2199516
        '''

        folds = []
        folds_y = []
        folds_inx = []

        for i in range(foldNum):
            folds.append([])
            folds_y.append([])
            folds_inx.append([])


        class_inxs = self.class_inxs
        
        for c_count in range(len(self.classes)):
            X_cls = self.X[class_inxs[c_count]]
            y_cls = self.y[class_inxs[c_count]]


            #get the distant matrix for the current class
            dist_matrix_cls = self.dist_matrix_per_class[c_count]
            cls_inxs = class_inxs[c_count]

            
            cnt=len(X_cls)

            #while there are still samples left
            while(cnt>0): 

                #select first position
                pos = random.randint(0,len(X_cls)-1)
                sample = X_cls[pos]
                sample_y = y_cls[pos]


                folds[0].append(sample)
                folds_y[0].append(sample_y)
                folds_inx[0].append(cls_inxs[pos])
                
                
                
                cnt = cnt-1

                
                if(cnt==0):
                    break
                    
                
                #to each fold it will assign the closest sample to the sample in the pos index
                for i in range(1,foldNum):
                    #assign the closest sample
                    p2 = self.getClosest(pos,dist_matrix_cls)


                    #assign sample
                    folds[i].append(X_cls[p2])
                    folds_y[i].append(y_cls[p2])
                    folds_inx[i].append(cls_inxs[p2])


                    #delete the sample selected
                    X_cls = np.delete(X_cls, (p2), axis=0)
                    y_cls = np.delete(y_cls, (p2), axis=0)
                    cls_inxs = np.delete(cls_inxs, (p2), axis=0)

                    dist_matrix_cls = np.delete(dist_matrix_cls, (p2), axis=0)
                    dist_matrix_cls = np.delete(dist_matrix_cls, (p2), axis=1)

                    cnt = cnt-1

                    if(p2 < pos):
                        pos = pos-1
                    


                    if(cnt==0):
                        break

                if(cnt==0):
                    break    
                
                #for the last sample
                dist_matrix_cls = np.delete(dist_matrix_cls, (pos), axis=0)
                dist_matrix_cls = np.delete(dist_matrix_cls, (pos), axis=1)

                X_cls = np.delete(X_cls, (pos), axis=0)
                y_cls = np.delete(y_cls, (pos), axis=0)
                cls_inxs = np.delete(cls_inxs, (pos), axis=0)

        return folds,folds_y,folds_inx

    def MSSCV(self,foldNum=5):
        '''
        Function used to perform maximally shifted statified cross validation (MSSCV) [1], each fold will contain the same number of samples of each class, which
        makes sure to mitigate prior probability dataset shift. Additionally, this method also tries distributes samples so that each fold is has different as possible.
        ------
        Parameters:
        foldNum (int): Number of folds to split the dataset into. Default value of 5 folds.
        ------
        Returns:
        folds (numpy.array): An array of foldNum size containing the split dataset according to SCV. Each element of this array corresponds to a fold.
        folds_y (numpy.array): An array of foldNum size containing the class labels for the samples in each fold of the fold array. 
        folds_inx (numpy.array): An array of foldNum size containing the indexes of the samples (in relation to the complete dataset) in each fold of the fold array.
        ------
        References:
        [1] Jose Garcıa Moreno-Torres, Jose A. Saez, and Francisco Herrera. Study on the impact of
        partition-induced dataset shift on k-fold cross-validation. IEEE Transactions on Neural
        Networks and Learning Systems, 23(8):1304–1312, 2012b. doi: 10.1109/TNNLS.2012.2199516
        '''



        folds = []
        folds_y = []
        folds_inx = []
        

        class_inxs = self.class_inxs
       
        
        for i in range(foldNum):
            folds.append([])
            folds_y.append([])
            folds_inx.append([])

        #for each class
        for c_count in range(len(self.classes)):
            X_cls = self.X[class_inxs[c_count]]
            y_cls = self.y[class_inxs[c_count]]
            cls_inxs = class_inxs[c_count]

            #get the distance matrix for this class
            dist_matrix_cls = self.dist_matrix_per_class[c_count]
                
            i = 0
            cnt=len(X_cls)
            
            #select the first position
            pos = random.randint(0,len(X_cls)-1)
            sample = X_cls[pos]
            sample_y = y_cls[pos]

            while(cnt>1): 
                folds[i].append(sample)
                folds_y[i].append(sample_y)
                folds_inx[i].append(cls_inxs[pos])
                
                
                
                cnt = cnt-1

                #rotate through the folds at each iteration
                i = (i+1)%foldNum


                #remove from dataset
                X_cls = np.delete(X_cls, (pos), axis=0)
                y_cls = np.delete(y_cls, (pos), axis=0)
                cls_inxs = np.delete(cls_inxs, (pos), axis=0)


                #get the sample most distant to the current one, it will be assigned to the next fold
                new_pos = self.getMostDistant(pos,dist_matrix_cls)
                

                #remove form dist matrix
                dist_matrix_cls = np.delete(dist_matrix_cls, (pos), axis=0)
                dist_matrix_cls = np.delete(dist_matrix_cls, (pos), axis=1)
                

                if(new_pos > pos):
                    pos = new_pos-1
                else:
                    pos = new_pos

                sample = X_cls[pos]
                sample_y = y_cls[pos]

            folds[i].append(sample)
            folds_y[i].append(sample_y)        
            folds_inx[i].append(cls_inxs[pos])    

        return folds,folds_y,folds_inx