''' Adapted from https://github.com/simoninithomas/Deep_reinforcement_learning_Course/blob/master/Deep%20Q%20Learning/Doom/Deep%20Q%20learning%20with%20Doom.ipynb'''



from memory import Memory
import numpy as np
import random
import main
import tensorflow as tf
from network import DQNetwork as net
import os
dir_path = os.path.dirname(os.path.realpath(__file__))



# Render the environment
main.setPreTraining(True)
training = True

### MODEL HYPERPARAMETERS
state_size = [5]      # Model input (Width, height) 
action_size = 4           # 4 possible actions: left, right, up, down
learning_rate =  0.0003      # Learning rate

### TRAINING HYPERPARAMETERS
batch_size = 128            

# Exploration parameters for epsilon greedy strategy
explore_start = 1.0            # exploration probability at start
explore_stop = 0.001            # minimum exploration probability 
decay_rate = 0.0001            # exponential decay rate for exploration prob

# Q learning hyperparameters
gamma = 0              # Discounting rate .95 -.98

### MEMORY HYPERPARAMETERS
pretrain_length = batch_size   # Number of experiences stored in the Memory when initialized for the first time
memory_size = 1000000          # Number of experiences the Memory can keep

memory = Memory(max_size = memory_size)
DQNetwork = net(state_size, 4, learning_rate)

def initialTrain():
    state = main.getData()
    main.startGame()
    # If it's the first step
    while not main.getDone():
        
        # Random action
        action = random.choice([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])
    
        # Get the rewards
        reward = main.getReward(action)
        # Look if the episode is finished
        done = main.getDone()
        
        # If we're dead
        if done:
            # We finished the episode
            next_state = np.zeros([5])
            
            # Add experience to memory
            memory.add((state, action, reward, next_state, done))
        
            
            # First we need a state
            state = main.getData()
            
            
            # Stack the frames
    
            
        else:
            # Get the next state
            next_state = main.getData()
            
            # Add experience to memory
            memory.add((state, action, reward, next_state, done))
            
            # Our state is now the next_state
            state = next_state
    main.initialize()


    train()        
            
def predict_action(explore_start, explore_stop, decay_rate, decay_step, state, actions, sess):
    global randomMoves, totalMoves
    ## EPSILON GREEDY STRATEGY
    # Choose action a from state s using epsilon greedy.
    ## First we randomize a number
    exp_exp_tradeoff = np.random.rand()

    # Here we'll use an improved version of our epsilon greedy strategy used in Q-learning notebook
    explore_probability = explore_stop + (explore_start - explore_stop) * np.exp(-decay_rate * decay_step)
    totalMoves+=1
    if (explore_probability > exp_exp_tradeoff):
        # Make a random action (exploration)
        action = random.choice([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])
        randomMoves += 1
        
        
    else:
        # Get action from Q-network (exploitation)
        # Estimate the Qs values state
        Qs = sess.run(DQNetwork.output, feed_dict = {DQNetwork.inputs_: [state]})
        
        # Take the biggest Q value (= the best action)
        choice = np.argmax(Qs)
        action = [0,0,0,0]
        action[int(choice)] = 1
                
    return action, explore_probability
    
    


writer = tf.summary.FileWriter("/tensorboard/dqn/1")

## Losses
tf.summary.scalar("Loss", DQNetwork.loss)

write_op = tf.summary.merge_all()

saver = tf.train.Saver()

        

def train():
    global randomMoves, totalMoves, gamma
    with tf.Session() as sess:
        # Initialize the variables
        sess.run(tf.global_variables_initializer())
        
        # Initialize the decay rate (that will use to reduce epsilon) 
        decay_step = 0
        if main.model != None:
            print("oh no")
            saver.restore(sess, main.model[0:-6])
            decay_step = 1000000
        # Init the game
        instance = 0
        while(training):
            # Set step to 0
            instance += 1

            
            # Initialize the rewards of the episode
            episode_rewards = []
            
            # Make a new episode and observe the first state
            main.startGame()
            if main.getPlaying() == False:
                        main.setPlaying(True)
            state = main.getData()
            randomMoves = 0
            totalMoves = 0
            while main.getPlaying():
                if main.ticks != 1000:
                    main.pygame.time.Clock().tick(main.ticks)

                
                # Increase decay_step
                decay_step +=1
                
                # Predict the action to take and take it
                action, explore_probability = predict_action(explore_start, explore_stop, decay_rate, decay_step, state, [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]], sess)

                # Do the action
                reward = main.getReward(action)

                # Look if the episode is finished
                done = main.getPlaying()
                
                # Add the reward to total reward
                episode_rewards.append(reward)

                # If the game is finished
                if not done:
                    # the episode ends so no next state
                    next_state = np.zeros((5), dtype=np.int)
                    



                    # Get the total reward of the episode
                    total_reward = np.sum(episode_rewards)

                    print('Episode: {}'.format(main.getGen()),
                              'Total reward: {:.4f}'.format(total_reward),
                              'Explore P: {:.4f}'.format(explore_probability),
                              'Moves: R:' , randomMoves, ' T:', totalMoves)

                    memory.add((state, action, reward, next_state, done))

                else:
                    # Get the next state
                    next_state =main.getData()
                    

                    # Add experience to memory
                    memory.add((state, action, reward, next_state, done))
                    
                    # st+1 is now our current state
                    state = next_state


                ### LEARNING PART            
                # Obtain random mini-batch from memory
                batch = memory.sample(batch_size)
                states_mb = np.array([each[0] for each in batch], ndmin=2)
                actions_mb = np.array([each[1] for each in batch])
                rewards_mb = np.array([each[2] for each in batch]) 
                next_states_mb = np.array([each[3] for each in batch], ndmin=2)
                dones_mb = np.array([each[4] for each in batch])

                target_Qs_batch = []
                 # Get Q values for next_state 
                Qs_next_state = sess.run(DQNetwork.output, feed_dict = {DQNetwork.inputs_: next_states_mb})
                
                # Set Q_target = r if the episode ends at s+1, otherwise set Q_target = r + gamma*maxQ(s', a')
                for i in range(0, len(batch)):
                    terminal = dones_mb[i]

                    # If we are in a terminal state, only equals reward
                    if terminal:
                        target_Qs_batch.append(rewards_mb[i])
                        
                    else:
                        target = rewards_mb[i] + gamma * np.max(Qs_next_state[i])
                        target_Qs_batch.append(target)
                        

                targets_mb = np.array([each for each in target_Qs_batch])

                loss, _ = sess.run([DQNetwork.loss, DQNetwork.optimizer],
                                    feed_dict={DQNetwork.inputs_: states_mb,
                                               DQNetwork.target_Q: targets_mb,
                                               DQNetwork.actions_: actions_mb})

                # Write TF Summaries
                summary = sess.run(write_op, feed_dict={DQNetwork.inputs_: states_mb,
                                                   DQNetwork.target_Q: targets_mb,
                                                   DQNetwork.actions_: actions_mb})
                writer.add_summary(summary, instance)
                writer.flush()

            # Save model every 10 episodes
            if instance % 100 == 0:
                save_path = saver.save(sess, dir_path + "/models/model" + str(instance)+ ".ckpt")
                print("Model Saved")
        
initialTrain()