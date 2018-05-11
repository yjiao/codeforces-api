from random import *

def getProblems():
	problems = []
	
	fname = '../problem_ratings.csv'
	with open(fname, 'r') as f:
		lines = f.read().split('\n')[1:-1]
		
		for line in lines:
			problem_data = line.split(',')
			problem_data[0] = int(problem_data[0])
			problem_data[2] = int(problem_data[2])
			
			problems.append(problem_data)
	
	return problems

def createSet(minR, maxR, n = 18, hn = 2, hard = 50, width = 100, jump = 40):
	problems = getProblems()
	
	for i in xrange(minR, maxR+1, jump):
				low = i
				high = i + width
				hardR = high + hard
				
				l1 = []
				l2 = []
				
				for p in problems:
					if low <= p[2] <= high:
						l1.append(p)
					elif high < p[2] < hardR:
						l2.append(p)
				
				l = sample(l1, n) + sample(l2, hn)
				l.sort(key = lambda x : x[2])
				
				out_filename = 'problem_ratings_' + str(low) + '_to_' + str(high) + '.txt'
								
				with open(out_filename, 'w') as f:
					for p in l:
						s = 'codeforces.com/contest/' + str(p[0]) + '/problem/' + p[1] + '\n'
						f.write(s)
				
				
				
				

if __name__ == '__main__':
	createSet(1000, 1400)	
	
		
