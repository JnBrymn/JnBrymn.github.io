---
layout: post
title: "The Brain's Amazing Ability to Process Stereo Sound"
---

There's a lot of amazing things about how the brain works, and in this post I'm going to explore the phenomenon of binaural hearing – that is, your brain's amazing ability to hear with both ears ("binaural"), combine the signals, and quickly extract useful information in a way that I think should basically be impossible for the slow meat-computer that it is. Crazy stuff! Here we go!


<figure style="text-align: center; width: 60%; height: 470px; overflow: hidden; margin: auto;">
  <img src="/assets/the-brain-is-a-binaural-interferometer/face.png" 
       alt="Face" 
       style="width: 100%; height: 100%; object-fit: cover; object-position: top;">
  <!-- <figcaption></figcaption> -->
</figure>





## Interferometry Basics

Let's get things started by considering two pure sinusoidal audio signals. The left signal is 220Hz and the right is 225Hz.

<figure style="text-align: center">
  <img src="/assets/the-brain-is-a-binaural-interferometer/sinusoidal_waveforms.png" alt="Sinusoidal Waves" style="width: 100%; margin: auto;">
  <!-- <figcaption>
  </figcaption> -->
</figure>

If you were to listen to a speaker playing these two sounds, you would probably assume that you would hear two tones that are obnoxiously just a bit off. However, this isn't the case. Instead, if you play both sounds simultaneously, the signals interfere with one another as shown here.

<figure style="text-align: center">
  <img src="/assets/the-brain-is-a-binaural-interferometer/sum_of_waveforms.png" alt="Sum of Waveforms" style="width: 100%; margin: auto;">
  <!-- <figcaption>
  </figcaption> -->
</figure>

The upper figure shows both signals plotted separately. Notice that a portion of the time the signals are in sync (e.g. they overlap), but because the frequencies are just a little bit off, they drift out of sync and when one signal is going up, the other is going low. When playing both signals simultaneously – for instance 220Hz in the left speaker and 225Hz in the right – the two waves interfere as shown in the lower figure. When the signals are in sync, the interference is constructive and the overall sound is louder. When the signals are out of sync, the interference is destructive and the sound is quieter. This effect is that you hear a single tone that is the average of the two, so 222.5Hz, and it pulses at the same frequency as the _difference_ of the two signals – in this case 5Hz.

<audio controls>
  <source src="/assets/the-brain-is-a-binaural-interferometer/binaural_beat.wav" type="audio/wav">
  Your browser does not support the audio element.
</audio>

Kinda soothing isn't it?

## There's Something Weird Here
Let's do an experiment. I want you to see something that I find amazing about the brain. Grab some earbuds or nice headphones and listen to the recording above. You should hear the same pulsing pattern that you heard earlier – so-called "binaural beats". Now listen to only one ear at a time – because each ear plays a pure tone, the pulsing effect goes away. (And if you have a good sense of pitch you'll notice that the left ear is just slightly deeper than the right.)

But the mystery here is why, with both earbuds in, you hear the pulsing pattern at all. Remember, the sound has to mix together for the effect to occur. If you're playing the sound without headphones, then the waves are mixing together in the physical medium of the air. But listening through earbuds, the only way that the two signals can mix together is if your brain is actually processing the signals and effectively adding them together. This is in fact what it's doing, but how on earth is it possible? For reference, sound moves through air at the speed of 343 m/s. But a signal moves through a neuron at about 1/3 of that speed, and every time the signal jumps from one neuron to the next there is an additional few milliseconds required to make the jump. So how is the brain able to coordinate signals coming in from opposite sides of the head, and calculate their interference pattern using circuitry that is significantly slower than physical phenomenon being measured? How on earth are you – _a binaural interferometer?_

## Why Are We Able to Do This?
I have no idea how our brains manage to combine sounds like this, but there are some distinct advantages to being able to process sound this accurately. The same processing that allows you to hear the binaural beats also makes it possible to very accurately locate the position of a noise based upon the time of arrival of the sound to each ear. If the source of a sound is directly in front of you, then the sound waves arrive to both ears at the same time, but if the source of the sound is to the right, then it takes a tiny fraction of a second longer for the sound to reach your left ear, and that difference is a clue to where the sound originates from. If you can accurately determine the source location of a sound, then you have the ability to look in the proper direction when you hear something stir in the brush. This, in turn, means getting eaten less often – thus this ability is quite useful for our survival!


## An Experiment to Test the Bounds of Binaural Processing
Just how far can we stretch this interesting ability? Well, let's do an experiment. I devised this when I was in college using MATLAB, but now since vibe coding allows me to write anything I want in a weekend, I finally got back around to reproducing it in a form that was a bit easier to share with others.

Here's the idea – I'm going to generate a bunch of vocal recordings of different readers reading various phrases. The phrases are common sayings, but modified a bit so that they are all of about the same length (a few seconds). Here's the challenge. I'm going to randomly pick 4 phrases and declare one of them to be "the secret phrase". It's your job to determine which phrase is "the secret phrase". Here's how it looks:

<figure style="text-align: center">
  <a href="https://binaural-chat.fly.dev/" target="_blank" rel="noopener noreferrer" >
    <img src="/assets/the-brain-is-a-binaural-interferometer/app_ui.png" alt="Binaural Chat App Interface" style="width: 60%; margin: auto;">
  </a>
</figure>

Naturally, there's a trick. We're going to employ our abilities as binaural interferometers to pick out the secret message. In the left ear, I will play all the phrases as they were originally produced. But in the right ear, I will invert the waveform of all the non-secret phrases. So, if you were a _perfect_ interferometer, then the waveforms for all the recordings would be added together, and the result would be that the non-secret messages completely canceled out and the only thing that you would hear is the secret message which would be at twice the normal volume.

Want to take the challenge? Click here. Make sure you're wearing earbuds or headphones for this!

<div style="text-align: center; margin: 2em;">
  <a href="https://binaural-chat.fly.dev/" target="_blank" rel="noopener noreferrer" style="display: inline-block; padding: 1em 2em; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">Take the Secret Phrase Challenge</a>
</div>

How did you do? For me, I'm clearly not a perfect interferometer (and I doubt you are either). The sound is still a jumbled mess of voices. _However_, one voice typically stands out. I can't explain why it stands out, it's just more coherent. It's in the center of my awareness, whereas the others feel like they are at the periphery. And so long as I don't read the phrases first, I can correctly select the secret message almost 100% of the time. (If you have a different experience, then spend a few minutes on it and I think your brain might adjust. And then you'll feel just as weird as I do about my new psychic-feeling power.)

_[By the way, here's the application code.](https://github.com/JnBrymn/binaural-chat) Remix it and make something even cooler._

## Is it Really _That_ Weird?

Yes. It is.

Ok, if you don't have the same bizarre accuracy with the challenge that I do, then I guess you won't be so impressed. Some people I've tested can't seem to find the groove. But if you do hear the secret message like I do, then you might say "It's not _that_ weird – you've inverted all the sounds, so of course they are going to sound different from the originals." Well, in that case, try taking the challenge with just the right earbud in – that's the one with the "distorted" sounds. You'll find that it is indistinguishable from the left ear bud when listened to in isolation, and the secret message disappears. All we have done is invert the waveform – it would be the same as just reversing the positive and negative terminals on your stereo – your ear doesn't care that the waveform is "upside down".

So what this means, is that your binaural processing is so _spectacularly_ accurate, that even when it's not presented with an "easy" constant tone (cf. the beginning of this post), your brain can still precisely calculate information about how two very complex waveforms relate to one another with millisecond accuracy. (The average human speaking voice is somewhere around 165Hz, which has a period of 6.06 milliseconds.) Even if it's not perfect interferometry, how does a slow computer made of meat even begin to accomplish this feat?

As you can see, _I'm terribly impressed._
