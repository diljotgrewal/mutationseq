# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 10:26:34 2013

@author: jtaghiyar
"""

from __future__ import division
import numpy
from math import log


class Features:
    def __init__(self, tumour_tuple=None, normal_tuple=None, reference_tuple=None, purity=70):
        self.name = "TCGA Benchmark 4 featureset with coverage info"
        self.version = "5_deep"
        self.tt = tumour_tuple
        self.nt = normal_tuple
        self.rt = reference_tuple
        
        if self.tt is None:
            self.tt = (None, [1]*6, [1]*6, [1]*6, [1]*6, [1]*6, 1, 1, 1, 1, 1, 1, None)

        if self.nt is None: 
            self.nt = (None, [1]*6, [1]*6, [1]*6, [1]*6, [1]*6, 1, 1, 1, 1, 1, 1, None)
        
        if self.rt is None:
            self.rt = (0, 0, 0, 0, 0)
            
        ## reference base index + 1 = index of the same base in the tumour/normal bam tuple
        self.b  = self.rt[0] + 1  
        
        ## coverage data        
        self.cd = (float(30), float(30), int(purity), float(0))
        
        ## to avoid division by zero
        self.ep = 1e-5 
        
        self.feature_set = (
        ("tumour_indels", self.tt[9] / self.tt[5][0]),
        ("normal_indels", self.nt[9] / self.nt[5][0]),
        ("tumour_entropy", self.tt[10]),
        ("normal_entropy", self.nt[10]),
        ("normal_tumour_entropy", self.nt[10] / (self.tt[10] + self.ep)),
        
        ("tumour_ref_depth", self.tt[self.b][0] / self.tt[5][0]),
        ("normal_ref_depth", self.nt[self.b][0] / self.nt[5][0]),
        ("normal_mapq_ratio", self.nt[5][2] / self.nt[5][0]),
        ("tumour_mapq_ratio", self.tt[5][2] / self.tt[5][0]),
        ("normal_ref_quality", self.nt[self.b][1] / self.nt[5][0]),
        ("tumour_ref_quality", self.tt[self.b][1] / self.tt[5][0]),
        ("normal_quality_ratio", self.nt[5][1] / self.nt[5][0]),
        ("tumour_quality_ratio", self.tt[5][1] / self.tt[5][0]),
        ("normal_distance_ratio", self.nt[5][3] / self.nt[5][0]),
        ("tumour_distance_ratio", self.tt[5][3] / self.tt[5][0]),
        
                
        ("normal_tumour_depth", (self.tt[5][0] / self.nt[5][0])),
        ("normal_tumour_quality", (self.tt[5][1] / self.tt[5][0]) / ((self.nt[5][1] / self.nt[5][0]) + self.ep)),
        ("normal_tumour_mapq", (self.tt[5][2] / self.tt[5][0]) / ((self.nt[5][2] / self.nt[5][0]) + self.ep)),
        ("normal_tumour_distance", (self.tt[5][3] / self.tt[5][0]) / ((self.nt[5][3] / self.nt[5][0]) + self.ep)),
        
        
        
        ("normal_tumour_ref_depth", ((self.tt[self.b][0] / self.tt[5][0]) + self.ep) / ((self.nt[self.b][0] / self.nt[5][0]) + self.ep)),
        ("normal_tumour_ref_mapq", ((self.tt[self.b][2] / (self.tt[self.b][0]+ self.ep)) + self.ep) / ((self.nt[self.b][2] / (self.nt[self.b][0]+ self.ep)) + self.ep)),
        ("normal_tumour_ref_quality", ((self.tt[self.b][1] / (self.tt[self.b][0]+ self.ep)) + self.ep) / ((self.nt[self.b][1] / (self.nt[self.b][0]+ self.ep)) + self.ep)),
        ("normal_tumour_ref_distance", ((self.tt[self.b][3] / (self.tt[self.b][0]+ self.ep)) + self.ep) / ((self.nt[self.b][3] / (self.nt[self.b][0]+ self.ep)) + self.ep)),        
        
        ("region_entropy", self.rt[4]),
        ("region_gc_content", self.rt[3]),
        ("homopolymer_f", self.rt[1]),
        ("homopolymer_b", self.rt[2]),
        
        
        ("normal_variant_depth_ratio", ((self.nt[5][0] - self.nt[self.b][0]) / self.nt[5][0])),
        ("tumour_variant_depth_ratio", ((self.tt[5][0] - self.tt[self.b][0]) / self.tt[5][0])),        
        ("tumour_variant_quality_ratio", ((self.tt[5][1] - self.tt[self.b][1]) / (self.tt[5][0] - self.tt[self.b][0] + self.ep))),
        ("normal_variant_quality_ratio", ((self.nt[5][1] - self.nt[self.b][1]) / (self.nt[5][0] - self.nt[self.b][0] + self.ep))),
        ("tumour_variant_quality", (self.tt[5][1] - self.tt[self.b][1])/self.tt[5][0]),
        ("normal_variant_quality", (self.nt[5][1] - self.nt[self.b][1])/self.nt[5][0]),
        ("normal_variant_distance", (self.nt[5][3] - self.nt[self.b][3]) / (self.nt[5][0] - self.nt[self.b][0] + self.ep)),
        ("tumour_variant_distance", (self.tt[5][3] - self.tt[self.b][3]) / (self.tt[5][0] - self.tt[self.b][0] + self.ep)),
        ("normal_variant_mapq_mean", (self.nt[5][2] - self.nt[self.b][2]) / (self.nt[5][0] - self.nt[self.b][0] + self.ep)),
        ("tumour_variant_mapq_mean", (self.tt[5][2] - self.tt[self.b][2]) / (self.tt[5][0] - self.tt[self.b][0] + self.ep)),
        #("normal_minor_allele", lambda t, n, r: (r[0] != t[7] and n[t[6] + 1][0] > 0) or (r[0] != t[6] and n[t[7] + 1][0] > 0)),
        
        
        
        ("normal_tumour_variant_depth_ratio", ((self.tt[5][0] - self.tt[self.b][0]) / self.tt[5][0]) / (((self.nt[5][0] - self.nt[self.b][0]) / self.nt[5][0]) + self.ep)),
        ("normal_tumour_variant_mapq_ratio", ((self.tt[5][2] - self.tt[self.b][2]) / (self.tt[5][0] - self.tt[self.b][0] + self.ep)) / ((self.nt[5][2] - self.nt[self.b][2]) / (self.nt[5][0] - self.nt[self.b][0] + self.ep) + self.ep)),
        ("normal_tumour_variant_quality_ratio", ((self.tt[5][1] - self.tt[self.b][1]) / (self.tt[5][0] - self.tt[self.b][0] + self.ep)) / ((self.nt[5][1] - self.nt[self.b][1]) / (self.nt[5][0] - self.nt[self.b][0] + self.ep) + self.ep)),
        ("normal_tumour_variant_distance_ratio", ((self.tt[5][3] - self.tt[self.b][3]) / (self.tt[5][0] - self.tt[self.b][0] + self.ep)) / ((self.nt[5][3] - self.nt[self.b][3]) / (self.nt[5][0] - self.nt[self.b][0] + self.ep) + self.ep)),
        )
        
        self.coverage_features = (
        ("tumour_contamination", self.cd[2] / 100),
        ("whole_genome", self.cd[3])
        )

    ##TODO: eventually this function should be removed    
    def __isvalid(self, x):
        if numpy.isnan(x) or numpy.isinf(x):
            
            ##TODO: remove this line
            print "NaN"
            return False
        return True
    
    def __xentropy(self):
        tumour_base_qualities = (self.tt[1][1], self.tt[2][1], self.tt[3][1], self.tt[4][1], self.tt[5][1])
        normal_base_qualities = (self.nt[1][1], self.nt[2][1], self.nt[3][1], self.nt[4][1], self.nt[5][1])
        total_tbq = tumour_base_qualities[4]
        total_nbq = normal_base_qualities[4]
        ent = 0 # entropy
        
        if total_tbq == 0 or total_nbq == 0:
            return ent
            
        for i in xrange(4):
            tumour_base_probability = tumour_base_qualities[i] / total_tbq
            normal_base_probability = normal_base_qualities[i] / total_nbq            
            if tumour_base_probability != 0:
                if normal_base_probability == 0:
                    ent -= -7 * tumour_base_probability
                else:
                    ent -= log(normal_base_probability) * tumour_base_probability
        return ent
    
    def get_features(self):
        features = []
        for _, f in self.feature_set:
            if self.__isvalid(f):
                features.append(f)
            else:
                features.append(0)
       
        for _,f in self.coverage_features:
            if self.__isvalid(f):
                features.append(f)
            else:
                features.append(0)
        
        features.append(self.__xentropy())
        return features
       
    def get_feature_names(self):
        feature_names = []
        for n, _ in self.feature_set:
            feature_names.append(n)

        for n, _ in self.coverage_features:
            feature_names.append(n)
        
        return feature_names
