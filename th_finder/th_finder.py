class ThFinder:
    def __init__(self):
        pass

    def __cal_th(self):
        total_slo_pctg = self.slo_vio_count * 100 / self.itr
        print("slo vio. pctg: ", total_slo_pctg)

        step = 4
        if total_slo_pctg > 10:
            self.vm_th -= step
            self.pkt_th -= step

        if total_slo_pctg < 5:
            if self.itr % 2 == 0:
                self.vm_th += 2
            else:
                self.pkt_th += 2
        if self.vm_th >= 100:
            self.vm_th = 99

        if self.pkt_th >= 100:
            self.pkt_th = 99
        print("vm th: ", self.vm_th, "pkt th: ", self.pkt_th)
        return None




    """
    def __cal_th(self):
        df = self.df[self.df['p99']<=100]
        df['slo_guart'] = (df['p99'] <= 1).astype(int)

        X = df[['vm_util', 'pkt_util']]
        Y = df[['slo_guart']]
        
        clf = DecisionTreeClassifier(random_state=1234, max_depth=2, max_features=1, class_weight={
                                     0: 9, 1: 1}, max_leaf_nodes=3)
        scaler = StandardScaler()
        pipe = Pipeline(steps=[
            ("preprocessor", scaler),
            ("classifier", clf)
        ])

        X_train, X_test, y_train, y_test = train_test_split(X, Y,test_size=.8, random_state = 42) 
        X_train=pd.DataFrame(X_train)
        y_train=pd.DataFrame(y_train)
        pipe.fit(X_train, y_train)

        X_test = pd.DataFrame(X_test)
        y_test = pd.DataFrame(y_test)

        print("test score: %s" % pipe.score(X_test, y_test))

        expected = y_test
        predicted = pipe.predict(X_test)

        conf_matrix = classification_report(expected, predicted)
        print(conf_matrix)

        th = pipe[1].tree_.threshold
        feat = pipe[1].tree_.feature
        util_th = scaler.inverse_transform([th[:2],[0,0]])
        vm_th, pkt_th = [-1, -1]

        if feat[0] == 0:
            vm_th,pkt_th = util_th[0]
        elif feat[0] == feat[1]:
            if feat[0] == 0:
                vm_util = util_th[0][0]
                pkt_util = -1
            else:
                vm_util = -1
                pkt_util = util_th[0][1]
        else:
            pkt_th,vm_th = util_th[0]
        print('vm_th: ', vm_th)
        print('pkt_th: ',pkt_th)

        plt.clf()
        fig, ax = plt.subplots(figsize=(7, 7))
        plot_decision_regions(X_train.to_numpy(), y_train['slo_guart'].to_numpy(), clf=pipe)
        plt.xlabel('VM Util. (%)')
        plt.ylabel('PKT. Util (%)')
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig("threshold.png")
        
        return vm_th, pkt_th
    """


