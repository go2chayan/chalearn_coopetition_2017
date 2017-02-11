import csvimport pickleimport mathimport numpy as npimport randomimport scipyfrom os import listdirfrom os.path import isfile, joinfrom sklearn import linear_modelfrom sklearn.metrics import mean_squared_errorFACIAL_FEATURES = ["Pitch", "Yaw  ", "Roll ", "inBrL", "otBrL", "inBrR", "otBrR",                   "EyeOL", "EyeOR", "oLipH", "iLipH", "LipCDt"]TARGET_LABEL = "interview"def LoadTranscriptFile(transcription_file):  fp = open(transcription_file, "r")  transcripts = pickle.load(fp)  print "Number of transcripts:", len(transcripts)   return transcriptsdef LoadAnnotations(filepath):  fp = open(filepath, "r")  annotations = pickle.load(fp)  return annotations################# PRAAT FEATURES #################def ConvertPraatFileNameToKey(filename):  parts = filename.split(".")  category = parts[-1]  key_prefix = ".".join(parts[:-1])  return "".join([key_prefix, ".mp4"]), categorydef GetPraatFiles(input_dir):  """Returns a dictionary of prosodic features."""  # This dict should have 3 keys, each pointing to a second level dict storing all the  # files of that category (pitch, loud,   praat_files = {}  files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]  for f in files:    if f[0] == ".":      continue    video_key, category = ConvertPraatFileNameToKey(f)    if category not in praat_files:      praat_files[category] = {}    praat_files[category][video_key] = join(input_dir, f)  return praat_filesdef PraatValueFromLine(line):  parts = line.split(" = ")  return float(parts[1])  def GetListStatistics(input_list):  """Returns the min, max, mean, and standard deviation of the input list."""  stat = {}  stat["mean"] = np.mean(input_list)  stat["std"] = np.std(input_list)  stat["min"] = np.amin(input_list)  stat["max"] = np.amax(input_list)  return statdef ExtractFormantFeaturesFromSingleFile(filepath):  feature_dict = {}  with open(filepath, 'r') as f:    lines = f.readlines()    i = 0    while i < len(lines):      line = lines[i]      trimmed = line.lstrip().rstrip()      if (trimmed == "formant [1]:" or trimmed == "formant [2]:" or          trimmed == "formant [3]:"):        # Get frequency.        freq_key = trimmed + "freq"        freq_val = PraatValueFromLine(lines[i + 1].lstrip().rstrip())        feature_dict.setdefault(freq_key, []).append(freq_val)                # Get bandwidth.        bw_key = trimmed + "bw"        bw_val = PraatValueFromLine(lines[i + 2].lstrip().rstrip())        feature_dict.setdefault(bw_key, []).append(bw_val)        i += 3      else:        i += 1  output_feature= {}  for k in feature_dict:    stat = GetListStatistics(feature_dict[k])    for stat_k in stat:      feature_key = ":".join([k, stat_k])      output_feature[feature_key] = stat[stat_k]  return output_featuredef GetFormantFeatures(formant_files):  formant_features = {}  num_files = 0  for vid_key in formant_files:    num_files += 1    formant_features[vid_key] = ExtractFormantFeaturesFromSingleFile(      formant_files[vid_key])    if num_files % 1000 == 0:      print "Processed Formant files: ", num_files  return formant_featuresdef ExtractLoudnessFeaturesFromSingleFile(filepath):  feature_list = []  with open(filepath, 'r') as f:    lines = f.readlines()    i = 15 # The start offset line number.    while i < len(lines):      line = lines[i]      trimmed = line.lstrip().rstrip()      parts = trimmed.split(" = ")      feature_list.append(float(parts[-1]))      i += 1  output_feature= {}  stat = GetListStatistics(feature_list)  for stat_k in stat:    feature_key = ":".join(["loudness", stat_k])    output_feature[feature_key] = stat[stat_k]  return output_featuredef GetLoudnessFeatures(loudness_files):  loudness_features = {}  num_files = 0  for vid_key in loudness_files:    num_files += 1    loudness_features[vid_key] = ExtractLoudnessFeaturesFromSingleFile(      loudness_files[vid_key])    if num_files % 1000 == 0:      print "Processed Loudness files: ", num_files  return loudness_featuresdef ExtractPitchFeaturesFromSingleFile(filepath):  feature_dict = {}  with open(filepath, 'r') as f:    lines = f.readlines()    i = 0    while i < len(lines):      line = lines[i]      trimmed = line.lstrip().rstrip()      if (trimmed == "candidate [1]:"):        freq_key = "pitch:" + "freq"        freq_val = PraatValueFromLine(lines[i + 1].lstrip().rstrip())        feature_dict.setdefault(freq_key, []).append(freq_val)                # Get bandwidth.        strength_key = "pitch:" + "strength"        strength_val = PraatValueFromLine(lines[i + 2].lstrip().rstrip())        feature_dict.setdefault(strength_key, []).append(strength_val)        i += 3      else:        i += 1  output_feature= {}  for k in feature_dict:    stat = GetListStatistics(feature_dict[k])    for stat_k in stat:      feature_key = ":".join([k, stat_k])      output_feature[feature_key] = stat[stat_k]  return output_featuredef GetPitchFeatures(pitch_files):  pitch_features = {}  num_files = 0  for vid_key in pitch_files:    num_files += 1    pitch_features[vid_key] = ExtractPitchFeaturesFromSingleFile(      pitch_files[vid_key])    if num_files % 1000 == 0:      print "Processed Pitch files: ", num_files  return pitch_featuresdef ExtractPraatFeatures(praat_files):  formant_features = {}  loudness_features = {}  pitch_features = {}  for category in praat_files:    if category == "formant":      formant_features = GetFormantFeatures(praat_files[category])    elif category == "loud":      loudness_features = GetLoudnessFeatures(praat_files[category])    elif category == "pitch":      pitch_features = GetPitchFeatures(praat_files[category])  return formant_features, loudness_features, pitch_features  # Converts a filename containing facial features to the corresponding video key.def ConvertFaceFileNameToKey(filename):  if filename[-4:] == ".csv":    return filename[0:-4]  else:    print "ERROR in the facial feature file name..."    return Nonedef ReadFacialFeaturesForOneFile(filepath):  """Calculates the facial features for a single video - specified by the filepath."""  with open(filepath, 'rb') as csvfile:    facial_data = csv.DictReader(csvfile)    avg_facial_features = {}    num_frames = 0    for row in facial_data:      num_frames += 1      for feature in FACIAL_FEATURES:        if not row[feature]:          continue        avg_facial_features[feature] = avg_facial_features.setdefault(          feature, 0.0) + float(row[feature].lstrip().rstrip())    for feature in avg_facial_features:      avg_facial_features[feature] /= float(num_frames)  return avg_facial_features# A method that reads all facial fearture files and loads facial features.def ReadFacialFeatures(input_dir):  """Reads facial features for all the videos in a given directory."""  files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]  video_features = {}  num_files_processed = 0  for f in files:    if f[0] == ".":      continue    video_key = ConvertFaceFileNameToKey(f)    new_feature = ReadFacialFeaturesForOneFile(join(input_dir, f))    num_files_processed += 1    if (num_files_processed % 1000) == 0:      print "Facial feature files processed: ", num_files_processed    if len(new_feature) < len(FACIAL_FEATURES):      continue    video_features[video_key] = new_feature  return video_features  def ExtractTranscriptFeatures(transcripts):  word_features = {}  for k in transcripts:    words = transcripts[k].split(" ")    unique_words = {}    for w in words:      unique_words[w] = 1    word_features[k] = {}    word_features[k]["total_words"] = float(len(words))    word_features[k]["unique_words"] = float(len(unique_words))    word_features[k]["total_to_unique"] = float(len(words)) / float(len(unique_words))  return word_features          ###########################  ML Related Functions ################def SplitTrainingTestSet(x, y, ind, ind_bar):  """Split the data into training and test sets."""  ytest = list();  ytrain = list();  xtest = list();  xtrain = list();  for i in ind:    xtrain.append(x[i])    ytrain.append(y[i])  for i in ind_bar:    xtest.append(x[i])    ytest.append(y[i])  return (ytrain,xtrain,ytest,xtest)def GetPartitionedIndices(n, ratio):  training_size = int(n * ratio)  randindices = random.sample(range(1, n), training_size)  ind = []  for i in randindices:    ind.append(i)  ind_bar = list(set(range(0, n)) - set(ind));  return ind, ind_bardef CombineFeatures(feature_dicts):  result = set(feature_dicts[0].keys())  for d in feature_dicts[1:]:    key_set = set(d.keys())    result &= key_set  print "Intersection size: " , len(result)  comb_features = {}  for k in result:    comb_features[k] = {}    for feature_dict in feature_dicts:      for f_key in feature_dict[k]:        comb_features[k][f_key] = feature_dict[k][f_key]  return comb_features    def GetFeatureAndLabelArraysFromDictionaries(D_features, D_labels):  X = []  y = list()  for k in sorted(D_features):    Xrow = list()    for f in sorted(D_features[k]):      Xrow.append(D_features[k][f])    X.append(Xrow)    y.append(D_labels[k])  print len(X)  print len(y)  return X, ydef AccuracyMetrics(ypredict, ytrue):  # Estimate correlation coefficients  corrval = np.corrcoef(np.array(ytrue), np.array(ypredict))  correlation = corrval[0][1]        # Estimate RMS Error  rms_error = math.sqrt(mean_squared_error(np.array(ytrue), np.array(ypredict)))        # Estimate Normalized RMS  datarange = np.amax(np.array(ytrue)) - np.amin(np.array(ytrue))  normalized_rms = rms_error/datarange  return correlation, rms_error, normalized_rmsdef main():  # Load the transcripts and calculate word features from transcripts.  training_transcripts = LoadTranscriptFile(    "../data/transcription_training.pkl")  training_word_features = ExtractTranscriptFeatures(training_transcripts)    # Read prosodic features.  praat_files = GetPraatFiles("../data/Audio")  training_formant, training_loudness, training_pitch = ExtractPraatFeatures(    praat_files)    # Read facial features.  training_facial_features = ReadFacialFeatures("../data/facial_features")  features_combined = CombineFeatures([training_word_features,                                       training_facial_features,                                       training_formant, training_loudness,                                       training_pitch])    # Read annotations/labels for training.  training_labels = LoadAnnotations("../data/annotation_training.pkl")  print len(training_labels)  # Convert dictionaries into lists.  X, y = GetFeatureAndLabelArraysFromDictionaries(features_combined,                                                  training_labels[TARGET_LABEL])  ind, ind_bar = GetPartitionedIndices(len(y), 0.8)  (ytrain,xtrain,ytest,xtest) = SplitTrainingTestSet(X,y,ind,ind_bar)  print len(ytrain), len(xtrain), len(ytest), len(xtest)  lasso = linear_model.Lasso(alpha=0.001, fit_intercept=True, normalize=False, precompute='auto', copy_X=True, max_iter=1000, tol=0.0001, warm_start=False, positive=False)  lasso.fit(xtrain, ytrain)  yp = lasso.predict(xtest)  for i in range(len(ytest)):    print yp[i], ytest[i]  corr, rms, norm_rms = AccuracyMetrics(yp, ytest)  print corr, rms, norm_rms###################################      if method == "lasso":##        lasso = linear_model.Lasso(alpha=0.05, fit_intercept=True, normalize=False, precompute='auto', copy_X=True, max_iter=1000, tol=0.0001, warm_start=False, positive=False)##        lasso.fit(X_train, ytrain)##        yp = lasso.predict(X_test)##        nfeatures = len(X_train[0])##        if iter == 0:##          weights = [0.0] * nfeatures##        ##        for jj in range(len(weights)):##          weights[jj] = weights[jj] + (lasso.coef_[jj])/float(nIters)################################################if __name__ == "__main__":  main()